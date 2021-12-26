import os
try:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
except Exception as e:
    print(e)
from apps.dowel_profiles import models
from PySide2 import QtWidgets
from view_managers.dovetail_modules.dowel_profile.dowel_profile_widget import ProfileListWidget
from view_managers.dovetail_modules.dowel_profile.dowel_list_widget import DowelListWidget
from models import MeasureUnitType

class DowelProfileManager(QtWidgets.QStackedWidget):
    def __init__(self, footer_btn=""):
        super(DowelProfileManager, self).__init__()
        self.__footer_btn_text = "Dowel Profiles" if len(footer_btn) == 0 else footer_btn
        self.dowel_profile_widget = ProfileListWidget()
        self.dowel_joint_widget = DowelListWidget()
        self.addWidget(self.dowel_profile_widget)
        self.addWidget(self.dowel_joint_widget)
        self.dowel_profile_widget.profileClicked.connect(self.load_dowel_joints)
        self.dowel_joint_widget.backSignal.connect(lambda :self.setCurrentIndex(0))
        self.profileChanged = self.dowel_profile_widget.profilesChanged

    def load_dowel_joints(self, profile_id):
        dowel_profile = models.DowelProfile.objects.get(pk= profile_id)
        self.dowel_joint_widget.load_dowels(dowel_profile)
        self.setCurrentIndex(1)

    def get_footer_btn_name(self) -> str:
        return self.__footer_btn_text

    def get_loaded_profiles(self):
        return self.dowel_profile_widget.get_loaded_profiles()

    def change_measure_mode(self, unit: MeasureUnitType):
        pass


if __name__ == "__main__":
    from views import utils
    app = QtWidgets.QApplication([])
    w = DowelProfileManager()
    w.show()
    app.setStyleSheet(utils.load_app_style())
    app.exec_()

