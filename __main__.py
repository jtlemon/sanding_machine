import os
import sys

try:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    from django.core.wsgi import get_wsgi_application

    application = get_wsgi_application()
except Exception as e:
    print(e)
import configurations.settings
from PySide2 import QtWidgets, QtGui, QtCore
from models import CameraMangerProcess
from view_managers import DovetailCameraPageManager, BitProfileManager, DowelJointProfileManager, \
    MachineSettingsManager, ResetPageManager, SandingPartProfilePageManager
from view_managers.sanding_camera_page_manager import ModifiedSandingPageManager
from view_managers.sanding_programs_operations.sanding_program_page import SandingProgramsPageManager
from view_managers.door_styles import SandingDoorStylesManager
from views import MachineInterfaceUi
from view_managers.sandpaper_management import SandingProfilePageManager
from configurations import static_app_configurations, AppSupportedOperations
import time
from models.temperature_service import TemperatureService
from models.sensors_connector_hal import SensorConnector
from models.grbl_hal import GrblControllerHal
from configurations.custom_pram_loader import CustomMachineParamManager
from view_managers.sander_management import SanderListingViewManagement
from custom_widgets.countdown_timer import CountDownTimerManager
from custom_widgets.spin_box import CustomSpinBox, SpinUnitMode
from models import MeasureUnitType
from apps.joint_profiles.models import JoinProfile
from apps.dowel_profiles.models import DowelProfile
from models.estop_serial_parser import EStopSerialInterface, SignalToModule
from configurations.system_configuration_loader import MainConfigurationLoader
from views import AlarmViewerDialog
from configurations import grbl_error_codes
from view_managers.change_bit_dialog import ChangeBitDialog
from view_managers import RetrieveMachinePramsDialog
from models.db_utils import is_bit_loaded, get_loaded_bit_name
from view_managers.utils import display_error_message
from custom_widgets.countdown_timer import CountDownTimerManager
from configurations.settings import CURRENT_MACHINE, SupportedMachines


class MachineGuiInterface(MachineInterfaceUi):
    def __init__(self):
        super(MachineGuiInterface, self).__init__()
        self.__current_machine_cycle = 0
        self.__camera_image_subscribers = {index: list() for index in
                                           range(static_app_configurations.AVAILABLE_CAMERAS)}
        self.__joint_dowel_profile_update_subscribers = set()
        self.__bit_profile_update_subscribers = set()
        self.__machine_setting_changed_subscribers = set()
        self.__installed_operations = {}
        self.__current_dowel_profile = None
        self.__current_bit_profile = None
        self.__current_joint_profile = None

        for app_operation in static_app_configurations.SUPPORTED_MACHINE_OPERATIONS:
            operation_page_widget = None
            if app_operation == static_app_configurations.AppSupportedOperations.dovetailCameraOperation:
                operation_page_widget = DovetailCameraPageManager("Camera")
                self.subscribe_to_image(0, operation_page_widget)
                self.__joint_dowel_profile_update_subscribers.add(operation_page_widget)
                self.__machine_setting_changed_subscribers.add(operation_page_widget)
            elif app_operation == AppSupportedOperations.sandingCameraOperations:
                operation_page_widget = ModifiedSandingPageManager("Camera")
                self.subscribe_to_image(0, operation_page_widget)
            elif app_operation == static_app_configurations.AppSupportedOperations.restMachineOperation:
                operation_page_widget = ResetPageManager()
                for cam_index in range(static_app_configurations.AVAILABLE_CAMERAS):
                    self.subscribe_to_image(cam_index, operation_page_widget)
            elif app_operation == static_app_configurations.AppSupportedOperations.jointDowelBitProfilesOperation:
                operation_page_widget = DowelJointProfileManager()
                operation_page_widget.profileChanged.connect(self.handle_joint_dowel_profile_updates)
            elif app_operation == static_app_configurations.AppSupportedOperations.bitProfilesOperation:
                operation_page_widget = BitProfileManager()
                operation_page_widget.profilesChanged.connect(self.handle_bit_profile_updates)
            elif app_operation == static_app_configurations.AppSupportedOperations.settingParametersOperation:
                operation_page_widget = MachineSettingsManager()
                operation_page_widget.settingChangedSignal.connect(self.handle_machine_setting_changed_slot)
            elif app_operation == static_app_configurations.AppSupportedOperations.partProfileOperation:
                operation_page_widget = SandingPartProfilePageManager()
            elif app_operation == static_app_configurations.AppSupportedOperations.sandingProgramsOperations:
                operation_page_widget = SandingProgramsPageManager()
            elif app_operation == static_app_configurations.AppSupportedOperations.individualSandPaperOperations:
                operation_page_widget = SandingProfilePageManager()
            elif app_operation == static_app_configurations.AppSupportedOperations.doorStylesOperation:
                operation_page_widget = SandingDoorStylesManager()
            elif app_operation == AppSupportedOperations.sandersManagementOperations:
                operation_page_widget = SanderListingViewManagement()
            elif app_operation == static_app_configurations.AppSupportedOperations.restMachineOperation:
                operation_page_widget = ResetPageManager()
            self.add_app_window_widget(operation_page_widget)
            self.__installed_operations[app_operation] = operation_page_widget

        # default
        self.__temperature_thread = TemperatureService()
        # display sensor values also and weight auto width, height in certain dovetail widget if it's existed
        self.__sensors_board_thread = SensorConnector()
        self.__grbl_interface = GrblControllerHal()
        self.__estop_interface = EStopSerialInterface()

        # connect signals
        self.measureUnitChangedSignal.connect(self.handle_measure_unit_changed)
        self.__temperature_thread.new_temperature.connect(
            lambda display_weather, weather_icon: self.set_current_temperature(display_weather, weather_icon))

        self.__sensors_board_thread.physicalErrorSignal.connect(self.__grbl_interface.handle_physical_error_signal)
        self.__sensors_board_thread.autoLeftRightWidthChanged.connect(
            self.__grbl_interface.handle_auto_left_right_width_changed)
        # this to control on/of servo
        self.__grbl_interface.servoStartSignal.connect(self.__sensors_board_thread.control_servo_state)
        self.__grbl_interface.machineStateChangedSignal.connect(self.handle_update_machine_state_lbl)
        if AppSupportedOperations.restMachineOperation in self.__installed_operations:
            reset_widget = self.__installed_operations[AppSupportedOperations.restMachineOperation]
            # reset widgets signal
            reset_widget.reset_controller_btn.clicked.connect(self.__grbl_interface.reset_machine)
            reset_widget.home_btn.clicked.connect(self.__grbl_interface.reset_and_home)
            if CURRENT_MACHINE == SupportedMachines.dovetailMachine:
                reset_widget.go_to_park_btn.clicked.connect(self.__grbl_interface.park)
                reset_widget.measure_tool_btn.clicked.connect(self.handle_measure_tool_clicked)
                reset_widget.serial_monitor_widget.monitorSendCmdSignal.connect(lambda cmd:
                                                                                self.__grbl_interface.grbl_stream.send_direct_command(
                                                                                    cmd,
                                                                                    clr_buffer=True
                                                                                ))
            reset_widget.serial_monitor_widget.errorReceivedSignal.connect(self.handle_new_error_decoded)
            self.__response_checker = QtCore.QTimer()
            self.__response_checker.setSingleShot(False)
            self.__response_checker.timeout.connect(self.get_latest_responses)
            self.__response_checker.start(200)

        # camera
        self.__camera_check_timer = QtCore.QTimer()
        self.__camera_check_timer.timeout.connect(self.check_available_images)
        self.__camera_check_timer.start(int(1000 / static_app_configurations.FRAME_RATE))

        # initiate all signals
        if AppSupportedOperations.jointDowelBitProfilesOperation in static_app_configurations.SUPPORTED_MACHINE_OPERATIONS:
            available_profile_names = self.__installed_operations[
                AppSupportedOperations.jointDowelBitProfilesOperation].get_loaded_profiles()
            self.handle_joint_dowel_profile_updates(available_profile_names)

        if AppSupportedOperations.bitProfilesOperation in static_app_configurations.SUPPORTED_MACHINE_OPERATIONS:
            available_profile_names = self.__installed_operations[
                AppSupportedOperations.bitProfilesOperation].get_loaded_profiles()
            self.handle_bit_profile_updates(available_profile_names)

        if AppSupportedOperations.dovetailCameraOperation in static_app_configurations.SUPPORTED_MACHINE_OPERATIONS:
            camera_widget_manager = self.__installed_operations[AppSupportedOperations.dovetailCameraOperation]
            camera_widget_manager.sideBtnClicked.connect(self.handle_side_buttons_changed)
            camera_widget_manager.startBtnClicked.connect(self.handle_soft_start_cycle)
            camera_widget_manager.cancelBtnClicked.connect(self.handle_soft_cancel_cycle)
            camera_widget_manager.measure_tool_btn.clicked.connect(self.handle_measure_tool_clicked)
            camera_widget_manager.change_bit_btn.clicked.connect(self.change_machine_bit)
            camera_widget_manager.selectedProfileChanged.connect(self.handle_selected_profile_changed)

        # start all threads
        self.__temperature_thread.start()
        self.__sensors_board_thread.start()
        self.__grbl_interface.start_process()
        self.__estop_interface.start()

        # load defaults
        self.load_defaults()

        # alarms
        self.latest_errors_container = list()
        self.header_error_lbl.mousePressEvent = self.handle_display_all_errors

        # check the bit state
        if is_bit_loaded():
            profile_name = get_loaded_bit_name()
            if profile_name is None:
                self.bit_not_loaded()
            else:
                camera_widget_manager = self.__installed_operations[AppSupportedOperations.dovetailCameraOperation]
                camera_widget_manager.loaded_bit_lbl.setText(f"loaded bit name :{profile_name}")

        else:
            self.bit_not_loaded()

        # init the loaded bit
        CustomMachineParamManager.set_value("left_active", 0)
        CustomMachineParamManager.set_value("right_active", 0)
        CustomMachineParamManager.store()

    def bit_not_loaded(self):
        pass

    def handle_measure_tool_clicked(self):
        self.__grbl_interface.measure_tool()

    def handle_new_error_decoded(self, category, color, error_key, error_text):
        self.latest_errors_container.append((error_key, error_text, color))
        self.header_error_lbl.set_error(category, preferred_color=color)

    def handle_display_all_errors(self, ev):
        if len(self.latest_errors_container):
            current_errors = self.latest_errors_container.copy()
            self.latest_errors_container.clear()
            dia = AlarmViewerDialog(current_errors, self)
            if dia.exec_():
                if len(self.latest_errors_container) == 0:
                    self.header_error_lbl.clr_errors()
            else:
                current_errors.extend(self.latest_errors_container)
                self.latest_errors_container = current_errors

    def get_latest_responses(self):
        reset_widget = self.__installed_operations[AppSupportedOperations.restMachineOperation]
        responses = self.__grbl_interface.get_latest_responses()
        reset_widget.serial_monitor_widget.response_received(responses)

    def load_defaults(self):
        target_unit = MeasureUnitType(MainConfigurationLoader.get_value("measure_unit", 1))
        self.handle_change_measure_unit(target_unit)
        self.switch_to_another_page(0)

    def handle_side_buttons_changed(self, left_lvl, right_lvl):
        left_value = static_app_configurations.DOVETAIL_LEFT_RIGHT_ACTIVE_LVL_MAPPER[left_lvl]
        right_value = static_app_configurations.DOVETAIL_LEFT_RIGHT_ACTIVE_LVL_MAPPER[right_lvl]
        CustomMachineParamManager.set_value("left_active", left_value)
        CustomMachineParamManager.set_value("right_active", right_value)

    def handle_selected_profile_changed(self, old_profile_name, new_profile_name):
        camera_widget_manager = self.__installed_operations[AppSupportedOperations.dovetailCameraOperation]
        profile_type, profile_name = new_profile_name.split("-")
        msg = QtWidgets.QMessageBox(self)
        msg.setIcon(QtWidgets.QMessageBox.Question)
        msg.setWindowTitle("change joint type")
        if len(old_profile_name) > 0:
            msg.setText(f"are you sure you want to change the joint type from {old_profile_name} to {new_profile_name}")
        else:
            msg.setText(f"are you sure you want to change the joint type to {new_profile_name}")
        msg.addButton(QtWidgets.QMessageBox.Yes)
        msg.addButton(QtWidgets.QMessageBox.No)
        if msg.exec_() == QtWidgets.QMessageBox.Yes:
            # self.__grbl_interface.set_fences()
            # @TODO send command to the machine
            if profile_type.lower().startswith("j"):
                target_profile = JoinProfile.objects.get(profile_name=profile_name)
                target_values = []
                for config_dict in static_app_configurations.DOVETAIL_JOINT_PROFILE_CONFIGURATION_MAIN:
                    target_values.append(target_profile.get_value(config_dict["target_key"]))
                camera_widget_manager.set_joint_prams(target_values)
                CustomMachineParamManager.set_value("loaded_profile_type", "joint")
            else:
                CustomMachineParamManager.set_value("loaded_profile_type", "dowel")
            self.__grbl_interface.set_fences()
        else:
            camera_widget_manager.reject_profile_change(old_profile_name)

    def handle_soft_start_cycle(self):
        camera_widget_manager = self.__installed_operations[AppSupportedOperations.dovetailCameraOperation]
        if is_bit_loaded():
            # validate that this the required bit for the profile
            profile_name_with_type = camera_widget_manager.get_selected_profile()
            profile_type, profile_name = profile_name_with_type.split("-")
            if profile_type.lower().startswith("j"):
                target_profile = JoinProfile.objects.get(profile_name=profile_name)
                joint_values = camera_widget_manager.get_joint_prams()
                camera_widget_manager.prams_stored()
                for index, config_dict in enumerate(
                        static_app_configurations.DOVETAIL_JOINT_PROFILE_CONFIGURATION_MAIN):
                    target_profile.set_value(config_dict["target_key"], joint_values[index])
                target_profile.save()
                CustomMachineParamManager.set_value("loaded_profile_type", "joint")
                CustomMachineParamManager.set_value("loaded_joint_profile_id", target_profile.pk)
            else:
                target_profile = DowelProfile.objects.get(profile_name=profile_name)
                CustomMachineParamManager.set_value("loaded_profile_type", "dowel")
                CustomMachineParamManager.set_value("loaded_dowel_profile_id", target_profile.pk)
            target_bit_profile_id = target_profile.bit_profile.pk
            loaded_bit_profile_id = CustomMachineParamManager.get_value("loaded_bit_id", -1)
            if loaded_bit_profile_id != target_bit_profile_id:
                camera_widget_manager.start_button.setChecked(False)
                display_error_message(
                    f"this profile requires {target_profile.bit_profile.profile_name} you have to load it first.")
                return
            camera_widget_manager.manage_start_cancel_active_state(True)
            if CountDownTimerManager.is_finished():
                if self.__current_machine_cycle == 0:
                    self.__grbl_interface.cycle_start_1()
                    self.__current_machine_cycle = 1
                    CountDownTimerManager.start(1)  # 10 sec
                elif self.__current_machine_cycle == 1:
                    self.__grbl_interface.cycle_start_2()
                    self.__current_machine_cycle = 0
                    camera_widget_manager.start_button.setChecked(False)
                    CountDownTimerManager.start(10)  # 5 sec
        else:
            display_error_message("bit must loaded first")
            camera_widget_manager.start_button.setChecked(False)

    def handle_soft_cancel_cycle(self):
        # change the buttons colors
        camera_widget_manager = self.__installed_operations[AppSupportedOperations.dovetailCameraOperation]
        camera_widget_manager.manage_start_cancel_active_state(False)
        # stop timer
        CountDownTimerManager.clear()
        # stop the actual machine
        self.__current_machine_cycle = 0
        self.__grbl_interface.cancel()

    def subscribe_to_image(self, index, widget):
        if index in self.__camera_image_subscribers:
            self.__camera_image_subscribers[index].append(widget)

    def change_machine_bit(self):
        self.__grbl_interface.park()
        dia = ChangeBitDialog()
        dia.callMeasureToolSignal.connect(lambda: self.__grbl_interface.measure_tool())
        self.__grbl_interface.newBitLengthCaptured.connect(lambda loaded_bit_length: dia.accept())
        if dia.exec_():
            bit_profile = dia.get_selected_bit_profile()
            profile_name = bit_profile.profile_name
            CustomMachineParamManager.set_value("loaded_bit_id", bit_profile.pk, True)
            camera_widget_manager = self.__installed_operations[AppSupportedOperations.dovetailCameraOperation]
            camera_widget_manager.loaded_bit_lbl.setText(f"loaded bit name :{profile_name}")

    def check_available_images(self):
        for cam_index in range(static_app_configurations.AVAILABLE_CAMERAS):
            subscribers_list = self.__camera_image_subscribers[cam_index]
            if len(subscribers_list) > 0:
                active_widget = None
                for subscriber_widget in subscribers_list:
                    if self.get_current_active_widget() == subscriber_widget:
                        active_widget = subscriber_widget
                if active_widget is None:
                    continue
                image = camera_process.get_image(cam_index)
                if image is None:
                    continue
                # convert image to pix mab
                height, width, channel = image.shape
                bytes_per_line = 3 * width
                q_image = QtGui.QImage(image.data, width, height, bytes_per_line, QtGui.QImage.Format_RGB888)
                pix_map = QtGui.QPixmap.fromImage(q_image)
                active_widget.new_image_received(cam_index, pix_map)

    def handle_joint_dowel_profile_updates(self, new_profiles):
        for subscriber_widget in self.__joint_dowel_profile_update_subscribers:
            subscriber_widget.handle_joint_dowel_profile_updated(new_profiles)

    def handle_bit_profile_updates(self, new_profiles):
        for subscriber_widget in self.__bit_profile_update_subscribers:
            subscriber_widget.handle_bit_profile_updated(new_profiles)

    def handle_update_machine_state_lbl(self, new_state):
        self.machine_status_lbl.setText(new_state)

    def handle_measure_unit_changed(self, new_unit: MeasureUnitType):
        for spinbox in CustomSpinBox.class_objects:
            spinbox.set_display_mode(
                SpinUnitMode.MM_MODE if new_unit == MeasureUnitType.MM_UNIT else SpinUnitMode.IN_MODE)

        for opt in self.__installed_operations:
            widget = self.__installed_operations[opt]
            # check here ........................
            widget.change_measure_mode(new_unit)

    def handle_machine_setting_changed_slot(self):
        for widget in self.__machine_setting_changed_subscribers:
            widget.handle_setting_changed()

    def closeEvent(self, event) -> None:
        self.__temperature_thread.close_service()
        self.__sensors_board_thread.close_service()
        self.__grbl_interface.release_resources()
        self.__estop_interface.requestInterruption()


def create_default_records():
    from apps.sanding_machine.models import Sander
    available_sanders = Sander.objects.all()
    if not available_sanders.exists():
        Sander.objects.get_or_create(name="Sander1")
        Sander.objects.get_or_create(name="Sander2")
        Sander.objects.get_or_create(name="Sander3")
        Sander.objects.get_or_create(name="Sander4")


if __name__ == "__main__":
    from views import utils

    app = QtWidgets.QApplication(sys.argv)
    utils.load_app_fonts()
    app.setStyleSheet(utils.load_app_style())
    # create default records
    create_default_records()
    # start_dia = RetrieveMachinePramsDialog()
    # if start_dia.exec_():
    if True:
        camera_process = CameraMangerProcess()
        camera_process.daemon = True
        camera_process.start()
        # make sure that the selected bit id field exist

        machine_gui_interface = MachineGuiInterface()
        machine_gui_interface.showMaximized()
        app.exec_()
        camera_process.close_service()
        time.sleep(1)
    sys.exit(0)
