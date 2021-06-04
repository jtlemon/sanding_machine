import os
try:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
except Exception as e:
    print(e)
from apps.dowel_profiles import models
from PySide2 import QtWidgets, QtCore, QtGui
from view_managers.joint_profiles.joint_profile_manager import JointProfilesPageManager
from view_managers.dowel_profile.dowel_profile_manager import DowelProfileManager
from models import MeasureUnitType

class DowelJointProfileManager(QtWidgets.QTabWidget):
    profileChanged = QtCore.Signal(list)
    def __init__(self, footer_btn=""):
        super(DowelJointProfileManager, self).__init__()
        self.__footer_btn_text = "Joint/Dowel Profiles" if len(footer_btn) == 0 else footer_btn
        self.joint_profile_manager = JointProfilesPageManager()
        self.dowel_profile_manager = DowelProfileManager()
        self.addTab(self.joint_profile_manager, "Joint Profiles")
        self.addTab(self.dowel_profile_manager, "Dowel Profiles")
        self.joint_profile_manager.profileChanged.connect(lambda : self.profileChanged.emit(self.get_loaded_profiles()))
        self.dowel_profile_manager.profileChanged.connect(lambda: self.profileChanged.emit(self.get_loaded_profiles()))

    def load_dowel_joints(self, profile_id):
        dowel_profile = models.DowelProfile.objects.get(pk= profile_id)
        self.dowel_joint_widget.load_dowels(dowel_profile)
        self.setCurrentIndex(1)

    def get_footer_btn_name(self) -> str:
        return self.__footer_btn_text

    def get_loaded_profiles(self):
        joint_profiles = self.joint_profile_manager.get_loaded_profiles()
        dowel_profiles = self.dowel_profile_manager.get_loaded_profiles()
        loaded_profiles = list()
        for joint_profile in joint_profiles:
            loaded_profiles.append(f"J-{joint_profile}")
        for dowel_profile in dowel_profiles:
            loaded_profiles.append(f"D-{dowel_profile}")
        return loaded_profiles

    def change_measure_mode(self, unit: MeasureUnitType):
        pass


if __name__ == "__main__":
    from views import utils
    app = QtWidgets.QApplication([])
    w = DowelProfileManager()
    w.show()
    app.setStyleSheet(utils.load_app_style())
    app.exec_()

