import os

try:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    from django.core.wsgi import get_wsgi_application

    application = get_wsgi_application()
except Exception as e:
    print(e)
from apps.dowel_profiles import models
from PySide2 import QtWidgets
from view_managers.profiles_helper_functions import get_supported_profiles
from view_managers.dialog_configured_prams import RenderInternalPramsWidget
import configurations.static_app_configurations as static_configurations
from configurations.constants_types import AppSupportedOperations
from views.custom_app_widgets import SaveCancelButtons, QLineEditWithSideLabel
from apps.bit_profiles.models import BitProfile
from view_managers.utils import display_error_message



class AddEditDowelProfileDialog(QtWidgets.QDialog):
    def __init__(self, dowel_profile= None, parent=None):
        super(AddEditDowelProfileDialog, self).__init__(parent=parent)
        self.widget_layout = QtWidgets.QVBoxLayout(self)
        self.__dowel_profile = dowel_profile
        supported_dowels_profiles = get_supported_profiles(AppSupportedOperations.dowelsProfileOperation)
        profile_name = "" if dowel_profile is None else dowel_profile.profile_name
        self.profile_name_line_edit = QLineEditWithSideLabel("Profile Name", profile_name)
        self.widget_layout.addWidget(self.profile_name_line_edit)
        self.internal_prams_widget = RenderInternalPramsWidget(supported_dowels_profiles)
        self.widget_layout.addWidget(self.internal_prams_widget)
        if self.__dowel_profile:
            self.internal_prams_widget.load_initial_values(self.__dowel_profile.get_decoded_json())
        grid_layout = self.internal_prams_widget.layout()
        target_row = grid_layout.count()
        self.bit_profile_objects = BitProfile.objects.all()
        bit_profile_names = [bit_profile.profile_name for bit_profile in self.bit_profile_objects]
        lbl = QtWidgets.QLabel("Bit Profile")
        self.bit_combo_box = QtWidgets.QComboBox()
        self.bit_combo_box.addItems(bit_profile_names)
        grid_layout.addWidget(lbl, target_row, 0, 1, 1)
        grid_layout.addWidget(self.bit_combo_box, target_row, 1, 1, 1)

        self.save_cancel_widget = SaveCancelButtons()
        self.widget_layout.addWidget(self.save_cancel_widget)
        self.save_cancel_widget.cancel_btn.clicked.connect(self.reject)
        self.save_cancel_widget.save_btn.clicked.connect(self.handle_save_payload)
        self.setMinimumWidth(600)

    def handle_save_payload(self):
        profile_name = self.profile_name_line_edit.text().strip()
        bit_profile_index = self.bit_combo_box.currentIndex()
        if bit_profile_index == -1:
            display_error_message("you have to add bit profile first", "bit profiles", self)
            return
        if len(profile_name) == 0:
            display_error_message("please select the profile name first", "profile name", self)
            return
        # make sure that the name is not exist
        if (
                self.__dowel_profile and profile_name != self.__dowel_profile.profile_name) or self.__dowel_profile is None:
            available_profiles = models.DowelProfile.objects.filter(profile_name=profile_name)
            if available_profiles.exists():
                display_error_message("choose another profile name", "name already exists", self)
                return
        new_configured_json = self.internal_prams_widget.get_widget_payload()
        if self.__dowel_profile is None:
            # create a new dowel
            self.__dowel_profile = models.DowelProfile(
                profile_name=profile_name,
                default_prams_json=new_configured_json,
                machine= static_configurations.CURRENT_MACHINE,
                bit_profile=self.bit_profile_objects[bit_profile_index]
            )
            self.__dowel_profile.save()
        else:
            current_payload = self.__dowel_profile.get_decoded_json()
            current_payload.update(new_configured_json)
            self.__dowel_profile.profile_name = profile_name
            self.__dowel_profile.default_prams_json = current_payload
            self.__dowel_profile.bit_profile = self.bit_profile_objects[bit_profile_index]
            self.__dowel_profile.save()
        self.accept()

    def get_profile(self):
        return self.__dowel_profile

if __name__ == "__main__":
    from views import utils
    app = QtWidgets.QApplication([])
    utils.load_app_fonts()
    #
    add_edit_dialog = AddEditDowelProfileDialog()
    app.setStyleSheet(utils.load_app_style())
    add_edit_dialog.exec_()
    app.exec_()
