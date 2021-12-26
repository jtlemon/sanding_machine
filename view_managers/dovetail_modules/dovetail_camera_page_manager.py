from PySide2 import QtWidgets, QtCore

import custom_widgets.spin_box
from models import MeasureUnitType
from view_managers.abs_operation_widget_manager import AbstractOperationWidgetManger
from views import DovetailCameraPageView
from configurations import common_configurations
from configurations import dovetail_configurations
from apps.joint_profiles.models import JoinProfile
from apps.dowel_profiles.models import DowelProfile
from models.db_utils import is_bit_loaded, get_loaded_bit_name
from view_managers.change_bit_dialog import ChangeBitDialog
from custom_widgets.countdown_timer import CountDownTimerManager
from view_managers.utils import display_error_message
from configurations.custom_pram_loader import CustomMachineParamManager
from configurations.system_configuration_loader import MainConfigurationLoader
from view_managers.dialog_configured_prams import widget_create_from_dict, set_field_value


class DovetailCameraPageManager(DovetailCameraPageView, AbstractOperationWidgetManger):
    selectedProfileChanged = QtCore.Signal(str, str)

    def __init__(self, grbl_ref):
        super(DovetailCameraPageManager, self).__init__()
        self.__footer_btn_text = "Camera"
        self.__grbl_interface = grbl_ref
        self.__current_machine_cycle = 0
        # create dynamic widgets
        self.internal_widgets = list()
        for config_dict in dovetail_configurations.DOVETAIL_JOINT_PROFILE_CONFIGURATION_MAIN:
            name, key, control_widget = widget_create_from_dict(config_dict)
            if isinstance(control_widget, custom_widgets.spin_box.CustomSpinBox):
                control_widget.setMinimumWidth(300)
            lbl = QtWidgets.QLabel(name)
            lbl.setWordWrap(True)
            self.joint_options_frame_layout.addWidget(lbl)
            self.joint_options_frame_layout.addWidget(control_widget)
            self.internal_widgets.append(control_widget)
            default_value = CustomMachineParamManager.get_value(key, None)
            if default_value is None:
                default_value = control_widget.value()
                CustomMachineParamManager.set_value(key, default_value, False)
            else:
                set_field_value(control_widget, default_value)
        CustomMachineParamManager.store()
        self.dowel_option_frame.setVisible(False)
        self.joint_options_frame.setVisible(False)
        # take ref to signal
        self.sideBtnClicked = self.side_buttons_widget.sideBtnClicked
        self.startBtnClicked = self.start_button.clicked
        self.cancelBtnClicked = self.cancel_Button.clicked
        # fix camera width
        rec = QtWidgets.QApplication.desktop().screenGeometry()
        width = rec.width()
        height = rec.height()
        required_height = height - 425
        required_width = int(1.5 * required_height)
        self.camera_display.setMaximumSize(required_width, required_height)
        self.load_mid_btn_text()
        # install signals
        self.joint_dowel_profile_combo.currentTextChanged.connect(self.check_if_profile_selected)
        self.start_button.setEnabled(False)
        self.__current_selected_profile_type = ""
        self.__current_selected_profile = ""

        # interface signals
        self.sideBtnClicked.connect(self.handle_side_buttons_changed)
        self.startBtnClicked.connect(self.handle_soft_start_cycle)
        self.cancelBtnClicked.connect(self.handle_soft_cancel_cycle)
        self.measure_tool_btn.clicked.connect(self.__grbl_interface.measure_tool)
        self.change_bit_btn.clicked.connect(self.change_machine_bit)
        self.selectedProfileChanged.connect(self.handle_selected_profile_changed)

        # init the loaded bit
        CustomMachineParamManager.set_value("left_active", 0)
        CustomMachineParamManager.set_value("right_active", 0)
        CustomMachineParamManager.store()

        # check the bit state
        if is_bit_loaded():
            profile_name = get_loaded_bit_name()
            if profile_name is None:
                self.bit_not_loaded()
            else:
                self.loaded_bit_lbl.setText(f"loaded bit name :{profile_name}")

        else:
            self.bit_not_loaded()

    def set_joint_prams(self, prams_list: list):
        for index, widget in enumerate(self.internal_widgets):
            widget.set_value_and_reset_state(prams_list[index])

    def get_joint_prams(self):
        prams = []
        for widget in self.internal_widgets:
            prams.append(widget.value())
        return prams

    def prams_stored(self):
        for widget in self.internal_widgets:
            widget.reset_state()

    def check_if_profile_selected(self, profile_text: str):
        if len(profile_text) == 0:
            self.start_button.setEnabled(False)
            self.dowel_option_frame.setVisible(False)
            self.joint_options_frame.setVisible(False)
        else:
            if profile_text.lower()[0] == "j":
                self.dowel_option_frame.setVisible(False)
                self.joint_options_frame.setVisible(True)
                self.__current_selected_profile_type = "J"
            else:
                self.dowel_option_frame.setVisible(True)
                self.joint_options_frame.setVisible(False)
                self.__current_selected_profile_type = "D"
            self.start_button.setEnabled(True)
        if profile_text != self.__current_selected_profile:
            self.selectedProfileChanged.emit(self.__current_selected_profile, profile_text)
            self.__current_selected_profile = profile_text

    def reject_profile_change(self, old_profile_name):
        self.__current_selected_profile = old_profile_name
        self.joint_dowel_profile_combo.setCurrentText(old_profile_name)

    def manage_start_cancel_active_state(self, is_start_active):
        if is_start_active:
            self.start_button.setChecked(True)
            self.cancel_Button.setChecked(False)
        else:
            self.start_button.setChecked(False)
            self.cancel_Button.setChecked(True)

    def get_selected_profile(self):
        return self.joint_dowel_profile_combo.currentText()

    def change_measure_mode(self, unit: MeasureUnitType):
        self.load_mid_btn_text(unit)

    def load_mid_btn_text(self, unit: MeasureUnitType = MeasureUnitType.MM_UNIT):
        base_key = common_configurations.BASE_LEVEL_CONFIGURATION_KEY
        for index, widget in enumerate(self.side_buttons_widget.button_widgets_list):
            if index == 0:
                continue
            target_key = f"{base_key}{index}"
            value = CustomMachineParamManager.get_value(target_key, None)
            if not (value is None):
                if unit == MeasureUnitType.IN_UNIT:
                    value = round(value / 25.4, 3)
                    disp_text = f"{value}\""
                else:
                    value = round(value, 2)
                    disp_text = f"{value}mm"
                widget.set_mid_btn_text(str(disp_text))

    def get_footer_btn_name(self) -> str:
        return self.__footer_btn_text

    def is_dirty(self) -> bool:
        return False

    def new_image_received(self, camera_index, pix_map):
        if camera_index == 0:
            self.camera_display.setPixmap(pix_map)

    def handle_joint_dowel_profile_updated(self, new_profiles):
        self.joint_dowel_profile_combo.load_new_options(new_profiles)

    def handle_setting_changed(self):
        target_unit = MeasureUnitType(MainConfigurationLoader.get_value("measure_unit", 1))
        self.load_mid_btn_text(target_unit)

    def handle_side_buttons_changed(self, left_lvl, right_lvl):
        left_value = common_configurations.DOVETAIL_LEFT_RIGHT_ACTIVE_LVL_MAPPER[left_lvl]
        right_value = common_configurations.DOVETAIL_LEFT_RIGHT_ACTIVE_LVL_MAPPER[right_lvl]
        CustomMachineParamManager.set_value("left_active", left_value)
        CustomMachineParamManager.set_value("right_active", right_value)

    def handle_soft_start_cycle(self):
        if is_bit_loaded():
            # validate that this the required bit for the profile
            profile_name_with_type = self.get_selected_profile()
            profile_type, profile_name = profile_name_with_type.split("-")
            if profile_type.lower().startswith("j"):
                target_profile = JoinProfile.objects.get(profile_name=profile_name)
                joint_values = self.get_joint_prams()
                self.prams_stored()
                for index, config_dict in enumerate(
                        dovetail_configurations.DOVETAIL_JOINT_PROFILE_CONFIGURATION_MAIN):
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
                self.start_button.setChecked(False)
                display_error_message(
                    f"this profile requires {target_profile.bit_profile.profile_name} you have to load it first.")
                return
            self.manage_start_cancel_active_state(True)
            if CountDownTimerManager.is_finished():
                if self.__current_machine_cycle == 0:
                    self.__grbl_interface.cycle_start_1()
                    self.__current_machine_cycle = 1
                    CountDownTimerManager.start(1)  # 10 sec
                elif self.__current_machine_cycle == 1:
                    self.__grbl_interface.cycle_start_2()
                    self.__current_machine_cycle = 0
                    self.start_button.setChecked(False)
                    CountDownTimerManager.start(10)  # 5 sec
        else:
            display_error_message("bit must loaded first")
            self.start_button.setChecked(False)

    def handle_soft_cancel_cycle(self):
        # change the buttons colors
        self.manage_start_cancel_active_state(False)
        # stop timer
        CountDownTimerManager.clear()
        # stop the actual machine
        self.__current_machine_cycle = 0
        self.__grbl_interface.cancel()

    def change_machine_bit(self):
        self.__grbl_interface.park()
        dia = ChangeBitDialog()
        dia.callMeasureToolSignal.connect(lambda: self.__grbl_interface.measure_tool())
        self.__grbl_interface.newBitLengthCaptured.connect(lambda loaded_bit_length: dia.accept())
        if dia.exec_():
            bit_profile = dia.get_selected_bit_profile()
            profile_name = bit_profile.profile_name
            CustomMachineParamManager.set_value("loaded_bit_id", bit_profile.pk, True)
            self.loaded_bit_lbl.setText(f"loaded bit name :{profile_name}")

    def handle_selected_profile_changed(self, old_profile_name, new_profile_name):
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
                for config_dict in dovetail_configurations.DOVETAIL_JOINT_PROFILE_CONFIGURATION_MAIN:
                    target_values.append(target_profile.get_value(config_dict["target_key"]))
                self.set_joint_prams(target_values)
                CustomMachineParamManager.set_value("loaded_profile_type", "joint")
            else:
                CustomMachineParamManager.set_value("loaded_profile_type", "dowel")
            self.__grbl_interface.set_fences()
        else:
            self.reject_profile_change(old_profile_name)

    def bit_not_loaded(self):
        raise NotImplemented("you have to implement this method to load the bit")