import os
try:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
except Exception as e:
    print(e)

from PySide2 import QtWidgets
import configurations.static_app_configurations as static_configurations
from apps.joint_profiles import models
from apps.bit_profiles.models import BitProfile
from custom_widgets.spin_box import CustomSpinBox
from view_managers.utils import display_error_message
import django
from apps.commons import SupportedMachines
from configurations.settings import CURRENT_MACHINE



class AddEditJoinProfile(QtWidgets.QDialog):
    def __init__(self, current_profile: models.JoinProfile = None, parent=None):
        super(AddEditJoinProfile, self).__init__(parent=parent)
        self.__current_profile = current_profile
        if CURRENT_MACHINE == SupportedMachines.dovetailMachine:
            supported_joint_profiles = static_configurations.DOVETAIL_JOINT_PROFILE_CONFIGURATION
        else:
            raise ValueError("not supported machine.......")
        self.widget_layout = QtWidgets.QVBoxLayout(self)
        self.grid_layout = QtWidgets.QGridLayout()
        self.grid_layout.addWidget(QtWidgets.QLabel("Profile Name"), 0, 0, 1, 1)
        self.profile_name_edit = QtWidgets.QLineEdit("" if current_profile is None else current_profile.profile_name)
        self.grid_layout.addWidget(self.profile_name_edit, 0, 1, 1, 1)
        self.joint_profiles_spinbox_widgets = list()
        for index, joint_config in enumerate(supported_joint_profiles):
            widget_range = joint_config.get("range")
            lbl_text = joint_config.get("lbl")
            target_key = joint_config.get("target_key")
            initial_value = widget_range[0] if current_profile is None else current_profile.get_value(target_key)
            if initial_value is None:
                initial_value = widget_range[0]
            spinbox_widget = CustomSpinBox(
                *widget_range,
                initial_mm=initial_value,
                disp_precession=2,
                numpad_title=lbl_text,
                target_config_key=target_key
            )
            lbl = QtWidgets.QLabel(lbl_text)
            lbl.setWordWrap(True)
            target_row = index + 1
            self.grid_layout.addWidget(lbl, target_row, 0, 1, 1)
            self.grid_layout.addWidget(spinbox_widget, target_row, 1, 1, 1)
            self.joint_profiles_spinbox_widgets.append(spinbox_widget)
        self.widget_layout.addLayout(self.grid_layout)
        self.bit_profile_objects = BitProfile.objects.all()
        bit_profile_names = [bit_profile.profile_name for bit_profile in self.bit_profile_objects]
        lbl = QtWidgets.QLabel("Bit Profile")
        self.bit_combo_box = QtWidgets.QComboBox()
        self.bit_combo_box.addItems(bit_profile_names)
        self.grid_layout.addWidget(lbl, target_row+1, 0, 1, 1)
        self.grid_layout.addWidget(self.bit_combo_box, target_row+1, 1, 1, 1)
        # save/cancel buttons
        self.save_btn = QtWidgets.QPushButton("Save")
        self.save_btn.setMinimumSize(200, 60)
        self.cancel_btn = QtWidgets.QPushButton("Cancel")
        self.cancel_btn.setMinimumSize(200, 60)
        self.footer_layout = QtWidgets.QHBoxLayout()
        h_spacer_item_1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding,
                                                QtWidgets.QSizePolicy.Preferred)
        h_spacer_item_2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding,
                                                QtWidgets.QSizePolicy.Preferred)
        self.footer_layout.addItem(h_spacer_item_1)
        self.footer_layout.addWidget(self.cancel_btn)
        self.footer_layout.addWidget(self.save_btn)
        self.footer_layout.addItem(h_spacer_item_2)
        self.widget_layout.addLayout(self.footer_layout)

        # signals
        self.cancel_btn.clicked.connect(self.reject)
        self.save_btn.clicked.connect(self.handle_save_profile)
        self.setMinimumWidth(600)

    def handle_save_profile(self):
        profile_name = self.profile_name_edit.text().strip()
        bit_profile_index = self.bit_combo_box.currentIndex()
        if bit_profile_index == -1:
            display_error_message("you have to add bit profile first", "bit profiles", self)
            return
        if len(profile_name) == 0:
            display_error_message("please select the profile name first", "profile name", self)
            return
        # make sure that the name is not exist
        if (self.__current_profile and profile_name != self.__current_profile.profile_name) or self.__current_profile is None:
            available_profiles = models.JoinProfile.objects.filter(profile_name=profile_name)
            if available_profiles.exists():
                display_error_message("choose another profile name", "name already exists", self)
                return
        json_data = {}
        for spin_box in self.joint_profiles_spinbox_widgets:
            json_data[spin_box.get_key()] = spin_box.value()
        if self.__current_profile:
            # needs update
            self.__current_profile.profile_name = profile_name
            current_payload = self.__current_profile.get_decoded_json()
            current_payload.update(json_data)
            self.__current_profile.json_payload = current_payload
            self.__current_profile.bit_profile = self.bit_profile_objects[bit_profile_index]
        else:
            self.__current_profile = models.JoinProfile(profile_name=profile_name, json_payload=json_data,
                                                        machine=CURRENT_MACHINE,
                                                        bit_profile=self.bit_profile_objects[bit_profile_index]
                                                        )
        try:
            self.__current_profile.save()
        except django.db.IntegrityError:
            display_error_message("joint profile name must be unique")
            return

        self.accept()

    def get_profile(self):
        return  self.__current_profile


if __name__ == "__main__":
    from views import utils
    app = QtWidgets.QApplication([])
    utils.load_app_fonts()
    #
    add_edit_dialog = AddEditJoinProfile(models.JoinProfile.objects.last())
    app.setStyleSheet(utils.load_app_style())
    add_edit_dialog.exec_()
    app.exec_()

