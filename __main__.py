import os
import sys

try:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    from django.core.wsgi import get_wsgi_application

    application = get_wsgi_application()
except Exception as e:
    print(e)

from PySide2 import QtWidgets, QtGui, QtCore
from models import CameraMangerProcess
from view_managers import  DovetailCameraPageManager, BitProfileManager, DowelJointProfileManager, MachineSettingsManager, ResetPageManager
from views import MachineInterfaceUi
from configurations import static_app_configurations, AppSupportedOperations
import time
from models.temperature_service import TemperatureService
from models.sensors_connector_hal import SensorConnector
from models.grbl_hal import GrblControllerHal
from configurations.custom_pram_loader import CustomMachineParamManager
from custom_widgets.countdown_timer import CountDownTimerManager
from custom_widgets.spin_box import CustomSpinBox, SpinUnitMode
from models import MeasureUnitType
from apps.joint_profiles.models import JoinProfile
from apps.dowel_profiles.models import DowelProfile
from apps.bit_profiles.models import BitProfile
from models.estop_serial_parser import EStopSerialInterface, SignalToModule
from configurations.system_configuration_loader import MainConfigurationLoader



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
        for app_operation in static_app_configurations.SUPPORTED_OPERATIONS:
            operation_page_widget = None
            if app_operation == static_app_configurations.AppSupportedOperations.dovetailCameraOperation:
                operation_page_widget = DovetailCameraPageManager("Camera")
                self.subscribe_to_image(0, operation_page_widget)
                self.__joint_dowel_profile_update_subscribers.add(operation_page_widget)
                self.__machine_setting_changed_subscribers.add(operation_page_widget)
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
            reset_widget.serial_monitor_widget.monitorSendCmdSignal.connect(lambda cmd:
                                                                                 self.__grbl_interface.grbl_stream.send_direct_command(
                                                                                     cmd,
                                                                                     clr_buffer=True
                                                                                 ))
            self.__response_checker = QtCore.QTimer()
            self.__response_checker.setSingleShot(False)
            self.__response_checker.timeout.connect(self.get_latest_responses)
            self.__response_checker.start(200)

        # camera
        self.__camera_check_timer = QtCore.QTimer()
        self.__camera_check_timer.timeout.connect(self.check_available_images)
        self.__camera_check_timer.start(int(1000 / static_app_configurations.FRAME_RATE))

        # initiate all signals
        if AppSupportedOperations.jointDowelBitProfilesOperation in static_app_configurations.SUPPORTED_OPERATIONS:
            available_profile_names = self.__installed_operations[
                AppSupportedOperations.jointDowelBitProfilesOperation].get_loaded_profiles()
            self.handle_joint_dowel_profile_updates(available_profile_names)

        if AppSupportedOperations.bitProfilesOperation in static_app_configurations.SUPPORTED_OPERATIONS:
            available_profile_names = self.__installed_operations[
                AppSupportedOperations.bitProfilesOperation].get_loaded_profiles()
            self.handle_bit_profile_updates(available_profile_names)

        if AppSupportedOperations.dovetailCameraOperation in static_app_configurations.SUPPORTED_OPERATIONS:
            camera_widget_manager = self.__installed_operations[AppSupportedOperations.dovetailCameraOperation]
            camera_widget_manager.sideBtnClicked.connect(self.handle_side_buttons_changed)
            camera_widget_manager.startBtnClicked.connect(self.handle_soft_start_cycle)
            camera_widget_manager.cancelBtnClicked.connect(self.handle_soft_cancel_cycle)

        # start all threads
        self.__temperature_thread.start()
        self.__sensors_board_thread.start()
        self.__grbl_interface.start_process()
        self.__estop_interface.start()

        # load defaults
        self.load_defaults()

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

    def handle_soft_start_cycle(self):
        if self.is_profiles_loaded():
            camera_widget_manager = self.__installed_operations[AppSupportedOperations.dovetailCameraOperation]
            camera_widget_manager.manage_start_cancel_active_state(True)
            if self.__current_machine_cycle == 0:
                self.__grbl_interface.cycle_start_1()
                self.__current_machine_cycle = 1
            elif self.__current_machine_cycle == 1:
                self.__grbl_interface.cycle_start_2()
                self.__current_machine_cycle = 2
            else:
                self.__current_machine_cycle = 0
                self.handle_soft_cancel_cycle()

    def is_profiles_loaded(self):
        camera_widget_manager = self.__installed_operations[AppSupportedOperations.dovetailCameraOperation]
        bit_profile_name = camera_widget_manager.get_bit_profile_name()
        joint_profile_name = camera_widget_manager.get_joint_profile_name()
        dowel_profile_name = camera_widget_manager.get_dowel_profile_name()
        if len(bit_profile_name) == 0 or len(joint_profile_name) == 0 or len(dowel_profile_name) == 0:
            # all profile should be selected
            return False
        # load the profiles
        new_profile_loaded = False
        if self.__current_dowel_profile is None or self.__current_dowel_profile.profile_name != dowel_profile_name:
            self.__current_dowel_profile = DowelProfile.objects.get(profile_name=dowel_profile_name)
            new_profile_loaded = True
        if self.__current_joint_profile is None or self.__current_joint_profile.profile_name != joint_profile_name:
            self.__current_joint_profile = JoinProfile.objects.get(profile_name=joint_profile_name)
            new_profile_loaded = True
        if self.__current_bit_profile is None or self.__current_bit_profile.profile_name != bit_profile_name:
            self.__current_bit_profile = BitProfile.objects.get(profile_name=bit_profile_name)
            new_profile_loaded = True
        if new_profile_loaded:
            self.__grbl_interface.update_machine_profiles(joint_profile=self.__current_joint_profile,
                                                          dowel_profile=self.__current_dowel_profile,
                                                          bit_profile=self.__current_bit_profile)
        # all fine
        return True

    def handle_soft_cancel_cycle(self):
        # change the buttons colors
        camera_widget_manager = self.__installed_operations[AppSupportedOperations.dovetailCameraOperation]
        camera_widget_manager.manage_start_cancel_active_state(False)
        # stop timer
        CountDownTimerManager.clear()
        # stop the actual machine
        self.__grbl_interface.cancel()

    def subscribe_to_image(self, index, widget):
        if index in self.__camera_image_subscribers:
            self.__camera_image_subscribers[index].append(widget)

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
            widget.change_measure_mode(new_unit)

    def handle_machine_setting_changed_slot(self):
        for widget in self.__machine_setting_changed_subscribers:
            widget.handle_setting_changed()

    def closeEvent(self, event) -> None:
        self.__temperature_thread.close_service()
        self.__sensors_board_thread.close_service()
        self.__grbl_interface.release_resources()
        self.__estop_interface.requestInterruption()


if __name__ == "__main__":
    from views import utils
    camera_process = CameraMangerProcess()
    camera_process.daemon = True
    camera_process.start()
    app = QtWidgets.QApplication(sys.argv)
    utils.load_app_fonts()
    machine_gui_interface = MachineGuiInterface()
    machine_gui_interface.showMaximized()
    app.setStyleSheet(utils.load_app_style())
    app.exec_()
    camera_process.close_service()
    time.sleep(1)
    sys.exit(0)
