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
from custom_widgets.spin_box import CustomSpinBox


class AddEditJoinProfile(QtWidgets.QDialog):
    def __init__(self, current_profile: models.JoinProfile = None, parent=None):
        super(AddEditJoinProfile, self).__init__(parent=parent)
        self.__current_profile = current_profile
        if static_configurations.CURRENT_MACHINE == static_configurations.SupportedMachines.dovetailMachine:
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
        profile_name = self.profile_name_edit.text()
        json_data = {}
        for spin_box in self.joint_profiles_spinbox_widgets:
            json_data[spin_box.get_key()] = spin_box.value()
        if self.__current_profile:
            # needs update
            self.__current_profile.profile_name = profile_name
            current_payload = self.__current_profile.get_decoded_json()
            current_payload.update(json_data)
            self.__current_profile.json_payload = current_payload
            self.__current_profile.save()
        else:
            self.__current_profile = models.JoinProfile(profile_name=profile_name, json_payload=json_data,
                                                        machine=static_configurations.CURRENT_MACHINE
                                                        )
            self.__current_profile.save()
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

