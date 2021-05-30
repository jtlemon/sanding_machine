import os

try:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    from django.core.wsgi import get_wsgi_application

    application = get_wsgi_application()
except Exception as e:
    print(e)
from apps.dowel_profiles import models
from PySide2 import QtWidgets
from view_managers.dialog_configured_prams import RenderInternalPramsWidget
import configurations.static_app_configurations as static_configurations
from views.custom_app_widgets import SaveCancelButtons


class AddEditDowelDialog(QtWidgets.QDialog):
    def __init__(self, dowel_profile, dowel=None, parent=None):
        super(AddEditDowelDialog, self).__init__(parent=parent)
        self.widget_layout = QtWidgets.QVBoxLayout(self)
        self.__current_dowel = dowel
        self.__dowel_profile = dowel_profile
        if static_configurations.CURRENT_MACHINE == static_configurations.SupportedMachines.dovetailMachine:
            supported_dowels_profiles = static_configurations.DOVETAIL_DOWEL_JOINT_PROFILE_CONFIGURATION
        else:
            raise ValueError("not supported machine.......")
        self.internal_prams_widget = RenderInternalPramsWidget(supported_dowels_profiles)
        self.widget_layout.addWidget(self.internal_prams_widget)
        if self.__current_dowel:
            # in edit mode
            self.internal_prams_widget.load_initial_values(self.__current_dowel.get_decoded_json())
        else:
            # new mode
            self.internal_prams_widget.load_initial_values(self.__dowel_profile.get_decoded_json())

        self.save_cancel_widget = SaveCancelButtons()
        self.widget_layout.addWidget(self.save_cancel_widget)
        self.save_cancel_widget.cancel_btn.clicked.connect(self.reject)
        self.save_cancel_widget.save_btn.clicked.connect(self.handle_save_payload)
        self.setMinimumWidth(600)

    def handle_save_payload(self):
        new_configured_json = self.internal_prams_widget.get_widget_payload()
        if self.__current_dowel is None:
            # create a new dowel
            self.__current_dowel = models.DowelJoint(
                profile=self.__dowel_profile,
                prams_json=new_configured_json
            )
            self.__current_dowel.save()
        else:
            current_payload = self.__current_dowel.get_decoded_json()
            current_payload.update(new_configured_json)
            self.__current_dowel.prams_json = current_payload
            self.__current_dowel.save()
        self.accept()

    def get_dowel(self):
        return self.__current_dowel


if __name__ == "__main__":
    from views import utils
    app = QtWidgets.QApplication([])
    utils.load_app_fonts()
    #
    last_profile = models.DowelProfile.objects.last()
    last_dowel = models.DowelJoint.objects.last()
    add_edit_dialog = AddEditDowelDialog(last_profile, dowel=last_dowel)
    app.setStyleSheet(utils.load_app_style())
    add_edit_dialog.exec_()
    app.exec_()
