import os

try:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    from django.core.wsgi import get_wsgi_application

    application = get_wsgi_application()
except Exception as e:
    print(e)
from apps.dowel_profiles import models
from PySide2 import QtWidgets
from view_managers.dowel_profile.utils import get_supported_profiles
from view_managers.dialog_configured_prams import RenderInternalPramsWidget
import configurations.static_app_configurations as static_configurations
from views.custom_app_widgets import SaveCancelButtons, QLineEditWithSideLabel


class AddEditDowelProfileDialog(QtWidgets.QDialog):
    def __init__(self, dowel_profile= None, parent=None):
        super(AddEditDowelProfileDialog, self).__init__(parent=parent)
        self.widget_layout = QtWidgets.QVBoxLayout(self)
        self.__dowel_profile = dowel_profile
        supported_dowels_profiles = get_supported_profiles()
        profile_name = "" if dowel_profile is None else dowel_profile.profile_name
        self.profile_name_line_edit = QLineEditWithSideLabel("Profile Name", profile_name)
        self.widget_layout.addWidget(self.profile_name_line_edit)
        self.internal_prams_widget = RenderInternalPramsWidget(supported_dowels_profiles)
        self.widget_layout.addWidget(self.internal_prams_widget)
        if self.__dowel_profile:
            self.internal_prams_widget.load_initial_values(self.__dowel_profile.get_decoded_json())
        self.save_cancel_widget = SaveCancelButtons()
        self.widget_layout.addWidget(self.save_cancel_widget)
        self.save_cancel_widget.cancel_btn.clicked.connect(self.reject)
        self.save_cancel_widget.save_btn.clicked.connect(self.handle_save_payload)
        self.setMinimumWidth(600)

    def handle_save_payload(self):
        profile_name = self.profile_name_line_edit.text()
        new_configured_json = self.internal_prams_widget.get_widget_payload()
        if self.__dowel_profile is None:
            # create a new dowel
            self.__dowel_profile = models.DowelProfile(
                profile_name=profile_name,
                default_prams_json=new_configured_json,
                machine= static_configurations.CURRENT_MACHINE
            )
            self.__dowel_profile.save()
        else:
            current_payload = self.__dowel_profile.get_decoded_json()
            current_payload.update(new_configured_json)
            self.__dowel_profile.default_prams_json = current_payload
            self.__dowel_profile.save()
        self.accept()

    def get_profile(self):
        return self.__dowel_profile

if __name__ == "__main__":
    from views import utils
    app = QtWidgets.QApplication([])
    utils.load_app_fonts()
    #
    add_edit_dialog = AddEditDowelProfileDialog(models.DowelProfile.objects.last())
    app.setStyleSheet(utils.load_app_style())
    add_edit_dialog.exec_()
    app.exec_()
