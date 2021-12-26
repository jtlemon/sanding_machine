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
from configurations.common_configurations import CURRENT_MACHINE



class AddEditPartProfileDialog(QtWidgets.QDialog):
    def __init__(self, part_profile= None, parent=None):
        super(AddEditPartProfileDialog, self).__init__(parent=parent)
        self.widget_layout = QtWidgets.QVBoxLayout(self)
        self.__part_profile = part_profile
        supported_parts_profiles = get_supported_profiles(AppSupportedOperations.partProfileOperation)
        profile_name = "" if part_profile is None else part_profile.profile_name
        self.profile_name_line_edit = QLineEditWithSideLabel("Profile Name", profile_name)
        self.widget_layout.addWidget(self.profile_name_line_edit)
        self.internal_prams_widget = RenderInternalPramsWidget(supported_parts_profiles)
        self.widget_layout.addWidget(self.internal_prams_widget)
        if self.__part_profile:
            self.internal_prams_widget.load_initial_values(self.__part_profile.get_decoded_json())
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
                self.__part_profile and profile_name != self.__part_profile.profile_name) or self.__part_profile is None:
            available_profiles = models.PartProfile.objects.filter(profile_name=profile_name)
            if available_profiles.exists():
                display_error_message("choose another profile name", "name already exists", self)
                return
        new_configured_json = self.internal_prams_widget.get_widget_payload()
        if self.__part_profile is None:
            # create a new dowel
            self.__part_profile = models.PartProfile(
                profile_name=profile_name,
                json_payload=new_configured_json,
                machine= CURRENT_MACHINE
            )
            print(new_configured_json)
        else:
            current_payload = self.__part_profile.get_decoded_json()
            current_payload.update(new_configured_json)
            self.__part_profile.profile_name = profile_name
            self.__part_profile.json_payload = current_payload
        try:
            self.__part_profile.save()
            print("part saved .................")
        except django.db.IntegrityError:
            display_error_message("dowel profile name must be unique")
            return

        self.accept()

    def get_profile(self):
        return self.__part_profile

if __name__ == "__main__":
    from views import utils
    app = QtWidgets.QApplication([])
    utils.load_app_fonts()
    #
    add_edit_dialog = AddEditPartProfileDialog()
    app.setStyleSheet(utils.load_app_style())
    add_edit_dialog.exec_()
    app.exec_()
