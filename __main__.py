import os
import sys

# import models.sander_generate

try:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    from django.core.wsgi import get_wsgi_application

    application = get_wsgi_application()
except Exception as e:
    print(e)
from PySide2 import QtWidgets, QtGui, QtCore
from models.sander_generate import Probe
from models import CameraMangerProcess
from models.sander_generate import generate
from view_managers.sanding_modules import (
    SandingDoorStylesManager,
    SandingProgramsPageManager,
    SanderListingViewManagement,
    SandingProfilePageManager,
    SandingCameraPageManager,
    SandingPartProfilePageManager
)
from view_managers.dovetail_modules import (
    BitProfileManager,
    DowelJointProfileManager,
    DovetailCameraPageManager
)
from models import (
    MeasureUnitType,
    CameraMangerProcess,
    TemperatureService,
    SensorConnector,
    SandingGRBLHalController,
    DovetailGRBLHalController
)

from view_managers import MachineSettingsManager, ResetPageManager
from views import MachineInterfaceUi
from configurations import AppSupportedOperations
import time

from custom_widgets.spin_box import CustomSpinBox, SpinUnitMode
from models.estop_serial_parser import EStopSerialInterface
from configurations.system_configuration_loader import MainConfigurationLoader
from views import AlarmViewerDialog

from configurations import common_configurations
from configurations.custom_pram_loader import CustomMachineParamManager
from view_managers import utils as view_manager_utils


class MachineGuiInterface(MachineInterfaceUi):
    def __init__(self, machine_supported_operations: list):
        super(MachineGuiInterface, self).__init__()
        self.__current_machine_cycle = 0
        self.__camera_image_subscribers = {index: list() for index in
                                           range(common_configurations.AVAILABLE_CAMERAS)}
        self.__joint_dowel_profile_update_subscribers = set()
        self.__bit_profile_update_subscribers = set()
        self.__machine_setting_changed_subscribers = set()
        self.__installed_operations = {}
        self.__current_dowel_profile = None
        self.__current_bit_profile = None
        self.__current_joint_profile = None
        # default
        self.__temperature_thread = TemperatureService()
        # display sensor values also and weight auto width, height in certain dovetail widget if it's existed
        self.__sensors_board_thread = SensorConnector()
        self.__sensors_board_thread.physicalStartSignal.connect(self.common_sanding_start)
        self.__is_left_sanding_running = False
        self.__is_right_sanding_running = False
        self.__grbl_interface = None
        if common_configurations.CURRENT_MACHINE == common_configurations.SupportedMachines.sandingMachine:
            self.__grbl_interface = SandingGRBLHalController()
        elif common_configurations.CURRENT_MACHINE == common_configurations.SupportedMachines.dovetailMachine:
            self.__grbl_interface = DovetailGRBLHalController()
        else:
            raise ValueError("not supported machine.")
        self.__estop_interface = EStopSerialInterface()

        # create dynamic pages........
        for app_operation in machine_supported_operations:
            operation_page_widget = None
            if app_operation == AppSupportedOperations.dovetailCameraOperation:
                operation_page_widget = DovetailCameraPageManager(grbl_ref=self.__grbl_interface)
                self.subscribe_to_image(0, operation_page_widget)
                self.__joint_dowel_profile_update_subscribers.add(operation_page_widget)
                self.__machine_setting_changed_subscribers.add(operation_page_widget)
            elif app_operation == AppSupportedOperations.sandingCameraOperations:
                operation_page_widget = SandingCameraPageManager("Camera")
                operation_page_widget.start_left_button.setCheckable(True)
                operation_page_widget.start_right_button.setCheckable(True)
                operation_page_widget.start_left_button.clicked.connect(self.handle_left_start)
                operation_page_widget.start_right_button.clicked.connect(self.handle_right_start)
                self.subscribe_to_image(0, operation_page_widget)
            elif app_operation == AppSupportedOperations.restMachineOperation:
                operation_page_widget = ResetPageManager(grbl_interface_ref=self.__grbl_interface, sensors_board_ref=self.__sensors_board_thread)
                for cam_index in range(common_configurations.AVAILABLE_CAMERAS):
                    self.subscribe_to_image(cam_index, operation_page_widget)
                operation_page_widget.serial_monitor_widget.errorReceivedSignal.connect(self.handle_new_error_decoded)
            elif app_operation == AppSupportedOperations.jointDowelBitProfilesOperation:
                operation_page_widget = DowelJointProfileManager()
                operation_page_widget.profileChanged.connect(self.handle_joint_dowel_profile_updates)
            elif app_operation == AppSupportedOperations.bitProfilesOperation:
                operation_page_widget = BitProfileManager()
                operation_page_widget.profilesChanged.connect(self.handle_bit_profile_updates)
            elif app_operation == AppSupportedOperations.settingParametersOperation:
                operation_page_widget = MachineSettingsManager()
                operation_page_widget.settingChangedSignal.connect(self.handle_machine_setting_changed_slot)
                operation_page_widget.probCalibrationValuesModifiedSignal.connect(self.handle_prob_calibration_values_modified)
            elif app_operation == AppSupportedOperations.partProfileOperation:
                operation_page_widget = SandingPartProfilePageManager()
            elif app_operation == AppSupportedOperations.sandingProgramsOperations:
                operation_page_widget = SandingProgramsPageManager()
            elif app_operation == AppSupportedOperations.individualSandPaperOperations:
                operation_page_widget = SandingProfilePageManager()
            elif app_operation == AppSupportedOperations.doorStylesOperation:
                operation_page_widget = SandingDoorStylesManager()
            elif app_operation == AppSupportedOperations.sandersManagementOperations:
                operation_page_widget = SanderListingViewManagement()
            self.add_app_window_widget(operation_page_widget)
            self.__installed_operations[app_operation] = operation_page_widget

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
        # camera
        self.__camera_check_timer = QtCore.QTimer()
        self.__camera_check_timer.timeout.connect(self.check_available_images)
        self.__camera_check_timer.start(int(1000 / common_configurations.FRAME_RATE))

        # initiate all signals
        if AppSupportedOperations.jointDowelBitProfilesOperation in machine_supported_operations:
            joint_dowel_widget = self.__installed_operations[AppSupportedOperations.jointDowelBitProfilesOperation]
            self.handle_joint_dowel_profile_updates(joint_dowel_widget.get_loaded_profiles())

        if AppSupportedOperations.bitProfilesOperation in machine_supported_operations:
            bit_profiles_widget = self.__installed_operations[AppSupportedOperations.bitProfilesOperation]
            self.handle_bit_profile_updates(bit_profiles_widget.get_loaded_profiles())

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

        self.pageSelectedSignal.connect(self.handle_page_selected)
        self.handle_page_selected(0)
        self.switch_to_another_page(6)

    def handle_page_selected(self, page_index):
        if page_index == 0:
            if common_configurations.CURRENT_MACHINE == common_configurations.SupportedMachines.sandingMachine:
                camera_widget_manager = self.__installed_operations[AppSupportedOperations.sandingCameraOperations]
                door_styles = self.__installed_operations[
                    AppSupportedOperations.doorStylesOperation].get_loaded_profiles()
                sanding_programs = self.__installed_operations[
                    AppSupportedOperations.sandingProgramsOperations].get_sanding_programs()
                current_door_style = camera_widget_manager.door_styles_combo.currentText()
                current_program = camera_widget_manager.sanding_programs_combo.currentText()
                camera_widget_manager.door_styles_combo.clear()
                camera_widget_manager.sanding_programs_combo.clear()
                camera_widget_manager.door_styles_combo.addItems(door_styles)
                camera_widget_manager.sanding_programs_combo.addItems(sanding_programs)
                camera_widget_manager.door_styles_combo.setCurrentText(current_door_style)
                camera_widget_manager.sanding_programs_combo.setCurrentText(current_program)

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

    def load_defaults(self):
        target_unit = MeasureUnitType(MainConfigurationLoader.get_value("measure_unit", 1))
        self.handle_change_measure_unit(target_unit)
        self.switch_to_another_page(0)

    def subscribe_to_image(self, index, widget):
        if index in self.__camera_image_subscribers:
            self.__camera_image_subscribers[index].append(widget)

    def check_available_images(self):
        for cam_index in range(common_configurations.AVAILABLE_CAMERAS):
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

        # change dim units

    def handle_machine_setting_changed_slot(self):
        for widget in self.__machine_setting_changed_subscribers:
            widget.handle_setting_changed()

    def closeEvent(self, event) -> None:
        self.__temperature_thread.close_service()
        self.__sensors_board_thread.close_service()
        self.__grbl_interface.release_resources()
        self.__estop_interface.requestInterruption()

    def handle_left_start(self):
        print("left btn clicked")
        self.common_sanding_start('left')

    def handle_right_start(self):
        print("right btn clicked")
        self.common_sanding_start('right')

    def common_sanding_start(self, side="left"):
        widget = self.__installed_operations[AppSupportedOperations.sandingCameraOperations]
        if side == "left":
            if not widget.start_left_button.isChecked():
                print ("enable button again ............")
                widget.start_left_button.setStyleSheet("color:red")
                return
            else:
                widget.start_left_button.setStyleSheet("color:green")
        if side == "right":
            if not widget.start_right_button.isChecked():
                widget.start_right_button.setStyleSheet("color:red")
                return
            else:
                widget.start_right_button.setStyleSheet("color:green")
        print("let's execute the code ..............")
        left_slab_selected = widget.left_slab_option.isChecked()
        right_slab_selected = widget.right_slab_option.isChecked()
        probing_on = widget.probing_option.isChecked()
        program_name = widget.sanding_programs_combo.currentText()
        door_style = widget.door_styles_combo.currentText()
        left_part_width, left_part_length, right_part_width, right_part_length = widget.get_part_dimensions()
        x_max_length = CustomMachineParamManager.get_value("x_max_length")
        y_max_width = CustomMachineParamManager.get_value("y_max_width")
        if not probing_on:
            if side == "left":
                if left_part_width == 0 or left_part_length == 0 and not probing_on:
                    print("you have to set the left part  diminutions first")
                    return
                width, length = left_part_width, left_part_length
            else:
                if right_part_width == 0 or right_part_length == 0:
                    print("you have to set the right part  diminutions first")
                    return
                width, length = right_part_width, right_part_length

            if width > y_max_width or length > x_max_length:
                print("part is too large")
                return
        else:
            # todo, call the sander_generate.probe.probe_part from here, poplulate part width and length for left or right
            print('we are probing the part')
            from models.sander_generate import Probe
            self.p_1 = Probe(self.__grbl_interface, in_calibration_mode=False, side=side)
            self.p_1.calibrationFailedSignal.connect(self.__handle_calibration_failed)
            self.p_1.partProbbeingFinishedSignal.connect(self._handle_executing_machine_cycle)
            self.p_1.start()

        CustomMachineParamManager.set_value("left_slab_selected", left_slab_selected, auto_store=False)
        CustomMachineParamManager.set_value("right_slab_selected", right_slab_selected, auto_store=False)
        CustomMachineParamManager.set_value("program_name", program_name, auto_store=False)
        CustomMachineParamManager.set_value("door_style", door_style, auto_store=True)
        print(f'style {left_slab_selected}')
        if not probing_on:
            self._handle_executing_machine_cycle(side, length, width)

    def _handle_executing_machine_cycle(self, side, length, width):
        if side == "left":
            CustomMachineParamManager.set_value("left_part_width", width, auto_store=False)
            CustomMachineParamManager.set_value("left_part_length", length, auto_store=False)
        else:
            CustomMachineParamManager.set_value("right_part_width", width, auto_store=False)
            CustomMachineParamManager.set_value("right_part_length", length, auto_store=False)
        print(f'{side} dims: {length}, {width}')
        CustomMachineParamManager.set_value("side", side, auto_store=True)
        # todo call the sanding generate
        print(f'you pressed the {side} button')

        g_commands = generate(sensors_board_ref=self.__sensors_board_thread)
        self.send_g_code(g_commands)



    def handle_prob_calibration_values_modified(self):
        # handle the change

        self.p = Probe(self.__grbl_interface, in_calibration_mode=True)
        self.p.calibrationFailedSignal.connect(self.__handle_calibration_failed)
        self.p.start()

    def __handle_calibration_failed(self):
        self.__grbl_interface.park()
        utils.display_error_message("Failed to calibrate probe", "error", self)

    def send_g_code(self, g_commands:list):
        for command in g_commands:
            self.__grbl_interface.grbl_stream.add_new_command(command)




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

    if common_configurations.CURRENT_MACHINE == common_configurations.SupportedMachines.dovetailMachine:
        from configurations.dovetail_configurations import SUPPORTED_DOVETAIL_OPERATIONS

        machine_supported_operations = SUPPORTED_DOVETAIL_OPERATIONS
    elif common_configurations.CURRENT_MACHINE == common_configurations.SupportedMachines.sandingMachine:
        from configurations.sanding_configuration import SUPPORTED_SANDING_OPERATIONS

        machine_supported_operations = SUPPORTED_SANDING_OPERATIONS
    else:
        raise ValueError("not supported machine type.")
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

        machine_gui_interface = MachineGuiInterface(machine_supported_operations)
        machine_gui_interface.show()
        app.exec_()
        camera_process.close_service()
        time.sleep(1)
    sys.exit(0)
