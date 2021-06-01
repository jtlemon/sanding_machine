from PySide2 import QtWidgets
from models import MeasureUnitType
from .abs_operation_widget_manager import AbstractOperationWidgetManger
from views import DovetailCameraPageView
import configurations.static_app_configurations as static_configurations
from configurations.custom_pram_loader import CustomMachineParamManager


class DovetailCameraPageManager(DovetailCameraPageView, AbstractOperationWidgetManger):
    def __init__(self, footer_btn):
        super(DovetailCameraPageManager, self).__init__()
        self.__footer_btn_text = footer_btn
        # take ref to signal
        self.sideBtnClicked = self.side_buttons_widget.sideBtnClicked
        self.startBtnClicked = self.start_button.clicked
        self.cancelBtnClicked = self.cancel_Button.clicked
        # fix camera width
        rec = QtWidgets.QApplication.desktop().screenGeometry()
        width = rec.width()
        height = rec.height()
        required_height = height - 375
        required_width = int(1.5*required_height)
        self.camera_display.setMaximumSize(required_width, required_height)
        self.load_mid_btn_text()
        # install signals
        self.bit_profile_combo.currentTextChanged.connect(self.check_if_all_profiles_selected)
        self.joint_profile_combo.currentTextChanged.connect(self.check_if_all_profiles_selected)
        self.dowel_profile_combo.currentTextChanged.connect(self.check_if_all_profiles_selected)
        self.start_button.setEnabled(False)

    def check_if_all_profiles_selected(self, profile):
        bit_profile =  self.bit_profile_combo.currentText()
        joint_profile = self.joint_profile_combo.currentText()
        dowel_profile = self.dowel_profile_combo.currentText()
        if len(bit_profile) == 0 or len(joint_profile) == 0 or len(dowel_profile) == 0:
            self.start_button.setEnabled(False)
        else:
            self.start_button.setEnabled(True)

    def get_bit_profile_name(self):
        return self.bit_profile_combo.currentText()

    def get_dowel_profile_name(self):
        return self.dowel_profile_combo.currentText()

    def get_joint_profile_name(self):
        return self.dowel_profile_combo.currentText()

    def manage_start_cancel_active_state(self, is_start_active):
        if is_start_active:
            self.start_button.setChecked(True)
            self.cancel_Button.setChecked(False)
        else:
            self.start_button.setChecked(False)
            self.cancel_Button.setChecked(True)

    def get_joint_profile_name(self):
        return self.joint_profile_combo.currentText()

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
                    value = f"{value}mm"
                widget.set_mid_btn_text(str(value))


    def get_footer_btn_name(self) -> str:
        return self.__footer_btn_text


    def is_dirty(self) -> bool:
        return False


    def new_image_received(self, camera_index, pix_map):
        if camera_index == 0:
            self.camera_display.setPixmap(pix_map)

    def handle_joint_profile_updated(self, new_profiles):
        self.joint_profile_combo.load_new_options(new_profiles)

    def handle_dowel_profile_updated(self, new_profiles):
        self.dowel_profile_combo.load_new_options(new_profiles)

    def handle_bit_profile_updated(self, new_profiles):
        self.bit_profile_combo.load_new_options(new_profiles)


