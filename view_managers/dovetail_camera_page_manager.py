from PySide2 import QtWidgets, QtCore

import custom_widgets.spin_box
from models import MeasureUnitType
from .abs_operation_widget_manager import AbstractOperationWidgetManger
from views import DovetailCameraPageView
import configurations.static_app_configurations as static_configurations
from configurations.custom_pram_loader import CustomMachineParamManager
from configurations.system_configuration_loader import MainConfigurationLoader
from view_managers.dialog_configured_prams import widget_create_from_dict, set_field_value

class DovetailCameraPageManager(DovetailCameraPageView, AbstractOperationWidgetManger):
    selectedProfileChanged = QtCore.Signal(str, str)
    def __init__(self, footer_btn):
        super(DovetailCameraPageManager, self).__init__()
        self.__footer_btn_text = footer_btn
        # create dynamic widgets
        self.internal_widgets = list()
        for config_dict in static_configurations.DOVETAIL_JOINT_PROFILE_CONFIGURATION_MAIN:
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
        required_width = int(1.5*required_height)
        self.camera_display.setMaximumSize(required_width, required_height)
        self.load_mid_btn_text()
        # install signals
        self.joint_dowel_profile_combo.currentTextChanged.connect(self.check_if_profile_selected)
        self.start_button.setEnabled(False)
        self.__current_selected_profile_type = ""
        self.__current_selected_profile = ""

    def set_joint_prams(self, prams_list:list):
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

    def check_if_profile_selected(self, profile_text:str):
        if len(profile_text) == 0 :
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

    def load_mid_btn_text(self, unit: MeasureUnitType=MeasureUnitType.MM_UNIT):
        base_key = static_configurations.BASE_LEVEL_CONFIGURATION_KEY
        for index, widget in enumerate(self.side_buttons_widget.button_widgets_list):
            if index == 0:
                continue
            target_key = f"{base_key}{index}"
            value = CustomMachineParamManager.get_value(target_key, None)
            if not(value is None):
                if unit == MeasureUnitType.IN_UNIT:
                    value = round(value/25.4, 3)
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



