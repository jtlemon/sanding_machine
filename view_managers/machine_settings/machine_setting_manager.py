from PySide2 import QtWidgets, QtCore, QtGui
import math, re
import configurations.static_app_configurations
from models import MeasureUnitType
from configurations.system_configuration_loader import MainConfigurationLoader
from configurations.custom_pram_loader import CustomMachineParamManager
from views.custom_app_widgets import CenterPagePushButton
from view_managers.profiles_helper_functions import get_supported_profiles
from view_managers.gif_player_dialog import ImagePlayerDialog
from configurations.constants_types import AppSupportedOperations
from view_managers.dialog_configured_prams import RenderInternalPramsWidget, set_field_value


def is_valid_zipcode(zip_code):
    zip_code= zip_code.replace(" ", "")

    regx = re.compile(r"^[0-9]{5}(?:-[0-9]{4})?$")
    return False if regx.match(zip_code) is None else True


class MachineSettingsManager(QtWidgets.QWidget):
    def __init__(self, footer_btn=""):
        super(MachineSettingsManager, self).__init__()
        self.__footer_btn_text = "Settings" if len(footer_btn) == 0 else footer_btn
        self.widget_layout = QtWidgets.QVBoxLayout(self)
        # create a ui
        self.top_layout = QtWidgets.QHBoxLayout()
        h_spacer_1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.top_layout.addItem(h_spacer_1)
        zip_code_fixed_lbl = QtWidgets.QLabel("zip code")
        self.top_layout.addWidget(zip_code_fixed_lbl , stretch=0)
        self.__current_zip_code_value = MainConfigurationLoader.get_zip_code_value()
        self.zip_code_line_edit = QtWidgets.QLineEdit(self.__current_zip_code_value)
        self.zip_code_line_edit.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.zip_code_line_edit.setMaxLength(7)
        self.top_layout.addWidget(self.zip_code_line_edit, stretch=0)
        h_spacer_2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.top_layout.addItem(h_spacer_2)
        self.widget_layout.addLayout(self.top_layout, stretch=0)

        self.top_layout_1 = QtWidgets.QHBoxLayout()
        h_spacer_3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.top_layout_1.addItem(h_spacer_3)
        time_format_fixed_lbl = QtWidgets.QLabel("time format")
        self.top_layout_1.addWidget(time_format_fixed_lbl, stretch=0)
        self.__current_time_format = MainConfigurationLoader.get_time_format_value()
        self.time24_option = QtWidgets.QRadioButton("24 hr")
        self.time12_option = QtWidgets.QRadioButton("12 hr")
        if self.__current_time_format == 24:
            self.time24_option.setChecked(True)
        else:
            self.time12_option.setChecked(True)
        self.top_layout_1.addWidget(self.time24_option, stretch=0)
        self.top_layout_1.addWidget(self.time12_option, stretch=0)
        h_spacer_4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.top_layout_1.addItem(h_spacer_4)
        self.widget_layout.addLayout(self.top_layout_1, stretch=0)
        # dynamic part
        supported_setting_options = get_supported_profiles(AppSupportedOperations.settingParametersOperation)
        # if the settings more than 5 split it in to cols
        self.left_setting_widget = None
        self.right_setting_widget = None
        self.all_widgets_ref = []
        if len(supported_setting_options) > 5 :
            mid_index = len(supported_setting_options)//2
            left_list = supported_setting_options[:mid_index]
            right_list = supported_setting_options[mid_index:]
            self.left_setting_widget = RenderInternalPramsWidget(left_list)
            self.right_setting_widget = RenderInternalPramsWidget(right_list)
            self.all_widgets_ref = self.left_setting_widget.get_internal_widgets_ref()
            self.all_widgets_ref.extend(self.right_setting_widget.get_internal_widgets_ref())

        else:
            self.left_setting_widget = RenderInternalPramsWidget(supported_setting_options)
            self.all_widgets_ref = self.left_setting_widget.get_internal_widgets_ref()
        self.mid_layout = QtWidgets.QHBoxLayout()
        self.mid_layout.addItem(QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed))
        self.mid_layout.addWidget(self.left_setting_widget)
        if self.right_setting_widget:
            self.mid_layout.addWidget(self.right_setting_widget)
        self.mid_layout.addItem(
            QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed))

        self.widget_layout.addLayout(self.mid_layout, alignment=QtCore.Qt.AlignCenter)
        v_spacer_1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        self.widget_layout.addItem(v_spacer_1)
        # save setting btn
        self.save_setting_btn = CenterPagePushButton("Save Changes")
        self.save_setting_btn.widget_btn.setMinimumSize(300, 60)
        self.save_setting_btn.clicked.connect(lambda : self.save_changes(True))
        self.widget_layout.addWidget(self.save_setting_btn, stretch=0)
        self.load_initial_values()

    def load_initial_values(self):
        has_missing_prams = False
        for control_widget in self.all_widgets_ref:
            key = control_widget.get_key()
            default = control_widget.value()
            value = CustomMachineParamManager.get_value(key, None)
            if value == None:
                has_missing_prams = True
                CustomMachineParamManager.set_value(key, default, False)
                value = default
            set_field_value(control_widget, value)
        if has_missing_prams:
            CustomMachineParamManager.store()

    def get_footer_btn_name(self) -> str:
        return self.__footer_btn_text

    def is_dirty(self) -> bool:
        dirty = False
        time_format = 24 if self.time24_option.isChecked() else 12
        if time_format != self.__current_time_format:
            dirty = True
        zip_code = self.zip_code_line_edit.text()
        if zip_code != self.__current_zip_code_value:
            dirty = True
        for control_widget in self.all_widgets_ref:
            key = control_widget.get_key()
            value = control_widget.value()
            saved_value = CustomMachineParamManager.get_value(key)
            if value != saved_value:
                dirty = True

        return dirty

    def save_changes(self, show_animation=True):
        saved_flag = True
        zip_code = self.zip_code_line_edit.text()
        if not is_valid_zipcode(zip_code):
            msg = QtWidgets.QMessageBox(self)
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setWindowTitle("zip code invalid")
            msg.setText("please enter valid zip code.")
            msg.exec_()
            return  False
        time_format = 24 if self.time24_option.isChecked() else 12
        self.__current_time_format = time_format
        self.__current_zip_code_value = zip_code
        MainConfigurationLoader.set_zip_code_value(zip_code, False)
        MainConfigurationLoader.set_time_format_value(time_format, True) # to save the configuration in the file
        for control_widget in self.all_widgets_ref:
            key = control_widget.get_key()
            value = control_widget.value()
            CustomMachineParamManager.set_value(key, value, False)
            set_field_value(control_widget, value)

        CustomMachineParamManager.store()
        if show_animation:
            animation_dialog = ImagePlayerDialog(":/icons/icons/tenor.gif", parent=self)
            animation_dialog.exec_()
        return saved_flag

    def discard_changes(self):
        if self.__current_time_format == 24:
            self.time24_option.setChecked(True)
        else:
            self.time24_option.setChecked(False)
        self.zip_code_line_edit.setText(self.__current_zip_code_value)
        self.load_initial_values()

    def display_store_changes(self):
        if self.is_dirty():
            allow_leave = False
            msg = QtWidgets.QMessageBox(self)
            msg.setIcon(QtWidgets.QMessageBox.Question)
            msg.setWindowTitle("setting changed")
            msg.setText("Do you want to save the changes in the setting page?")
            msg.addButton(QtWidgets.QMessageBox.Yes)
            msg.addButton(QtWidgets.QMessageBox.No)
            msg.addButton(QtWidgets.QMessageBox.Cancel)
            ans = msg.exec_()
            if ans == QtWidgets.QMessageBox.Yes:
                allow_leave = not self.save_changes(show_animation=False)
            elif ans == QtWidgets.QMessageBox.No:
                self.discard_changes()
                allow_leave = True
        else:
            allow_leave = True
        return allow_leave

    def change_measure_mode(self, unit: MeasureUnitType):
        pass







if __name__ == "__main__":
    from views import utils
    app = QtWidgets.QApplication([])
    w = MachineSettingsManager()
    w.show()
    app.setStyleSheet(utils.load_app_style())
    app.exec_()