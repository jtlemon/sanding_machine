import os

try:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    from django.core.wsgi import get_wsgi_application

    application = get_wsgi_application()
except Exception as e:
    print(e)
from apps.sanding_machine import models
from PySide2 import QtWidgets
from view_managers.profiles_helper_functions import get_supported_profiles
from view_managers.dialog_configured_prams import RenderInternalPramsWidget
from configurations.constants_types import AppSupportedOperations
from views.custom_app_widgets import SaveCancelButtons, QLineEditWithSideLabel
from view_managers.utils import display_error_message
import django
from configurations.settings import CURRENT_MACHINE




class AddEditDoorStyleDialog(QtWidgets.QDialog):
    def __init__(self, door_style_profile= None, parent=None):
        super(AddEditDoorStyleDialog, self).__init__(parent=parent)
        self.widget_layout = QtWidgets.QVBoxLayout(self)
        self.__door_style_profile = door_style_profile
        door_style_fields_list = get_supported_profiles(AppSupportedOperations.doorStylesOperation)
        profile_name = "" if door_style_profile is None else door_style_profile.profile_name
        self.profile_name_line_edit = QLineEditWithSideLabel("Profile Name", profile_name)
        self.widget_layout.addWidget(self.profile_name_line_edit)
        self.internal_prams_widget = RenderInternalPramsWidget(door_style_fields_list)
        self.widget_layout.addWidget(self.internal_prams_widget)
        if self.__door_style_profile:
            self.internal_prams_widget.load_initial_values(self.__door_style_profile.get_decoded_json())
        self.save_cancel_widget = SaveCancelButtons()
        self.widget_layout.addWidget(self.save_cancel_widget)
        self.save_cancel_widget.cancel_btn.clicked.connect(self.reject)
        self.save_cancel_widget.save_btn.clicked.connect(self.handle_save_payload)
        self.setMinimumWidth(600)

    def handle_save_payload(self):
        profile_name = self.profile_name_line_edit.text().strip()
        if len(profile_name) == 0:
            display_error_message("please select the profile name first", "profile name", self)
            return
        # make sure that the name is not exist
        if (
                self.__door_style_profile and profile_name != self.__door_style_profile.profile_name) or self.__door_style_profile is None:
            available_profiles = models.DoorStyle.objects.filter(profile_name=profile_name)
            if available_profiles.exists():
                display_error_message("choose another profile name", "name already exists", self)
                return
        new_configured_json = self.internal_prams_widget.get_widget_payload()
        if self.__door_style_profile is None:
            # create a new dowel
            self.__door_style_profile = models.DoorStyle(
                profile_name=profile_name,
                json_payload=new_configured_json,
                machine= CURRENT_MACHINE
            )
        else:
            current_payload = self.__door_style_profile.get_decoded_json()
            current_payload.update(new_configured_json)
            self.__door_style_profile.profile_name = profile_name
            self.__door_style_profile.json_payload = current_payload
        try:
            total_profile_width = new_configured_json.get("outside_edge_width", 0) + \
                                  new_configured_json.get("inside_edge_width", 0) + \
                                  new_configured_json.get("frame_width", 0)
            self.__door_style_profile.set_value("total_profile_width", total_profile_width)
            self.__door_style_profile.save()
        except django.db.IntegrityError:
            display_error_message("Door style profile name must be unique")
            return
        self.accept()

    def get_profile(self):
        return self.__door_style_profile

if __name__ == "__main__":
    from views import utils
    app = QtWidgets.QApplication([])
    utils.load_app_fonts()
    #
    add_edit_dialog = AddEditDoorStyleDialog()
    app.setStyleSheet(utils.load_app_style())
    add_edit_dialog.exec_()
    app.exec_()

