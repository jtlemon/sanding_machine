import os
try:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
except Exception as e:
    print(e)
from apps.joint_profiles import models
from PySide2 import QtWidgets, QtCore, QtGui
from view_managers.joint_profiles.add_edit_profile_dialog import  AddEditJoinProfile
import configurations.static_app_configurations as static_configurations
from models.custom_app_types import MeasureUnitType
from views.custom_app_widgets import ProfileAddEditWidget
from apps.commons import SupportedMachines
from configurations.settings import CURRENT_MACHINE
from view_managers.abs_operation_widget_manager import AbstractOperationWidgetManger





class SandingDoorStylesManager(ProfileAddEditWidget, AbstractOperationWidgetManger):
    profileChanged = QtCore.Signal(set)
    def __init__(self, footer_btn="Door Styles"):
        super(SandingDoorStylesManager, self).__init__([])
        self.__joint_profiles_names = set()
        self.__footer_btn_text = footer_btn
        supported_profiles = static_configurations.SANDPAPER_PROFILE

        # i will assume that i will divid the widgets into 2 cols
        self.widget_layout = QtWidgets.QVBoxLayout(self)
        self.header_layout = QtWidgets.QHBoxLayout()
        h_spacer_item_1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding,
                                                QtWidgets.QSizePolicy.Preferred)
        self.header_layout.addItem(h_spacer_item_1)
        self.add_profile_btn = QtWidgets.QPushButton("add new profile")
        self.add_profile_btn.setMinimumSize(300, 60)
        h_spacer_item_2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding,
                                                QtWidgets.QSizePolicy.Preferred)
        self.header_layout.addWidget(self.add_profile_btn)
        self.header_layout.addItem(h_spacer_item_2)
        self.widget_layout.addLayout(self.header_layout)
        # table section
        col_names = ["name"]
        self.target_db_keys = list()
        self.default_values = list()



    def reload_joint_profiles(self):
        # clear table
        self.widget_table.setRowCount(0)
        self.__joint_profiles_names = set()
        for joint_profile in models.JoinProfile.objects.filter(machine=CURRENT_MACHINE):
            self.append_joint_to_table(joint_profile)
            self.__joint_profiles_names.add(joint_profile.profile_name)
        self.profileChanged.emit(self.__joint_profiles_names)


    def handle_edit_profile(self, profile_id):
        profile = models.JoinProfile.objects.get(pk=profile_id)
        row_index = self.get_row_id(profile_id)
        dia = AddEditJoinProfile(profile)
        old_profile_name = profile.profile_name
        if dia.exec_():
            new_profile = dia.get_profile()
            new_profile_name = new_profile.profile_name
            self.append_joint_to_table(new_profile, row_index=row_index)
            if old_profile_name != new_profile_name:
                self.__joint_profiles_names.remove(old_profile_name)
                self.__joint_profiles_names.add(new_profile_name)
                self.profileChanged.emit(self.__joint_profiles_names)


    def handle_add_profile(self):
        dia = AddEditJoinProfile(parent=self)
        if dia.exec_():
            new_profile = dia.get_profile()
            self.append_joint_to_table(new_profile)
            self.__joint_profiles_names.add(new_profile.profile_name)
            self.profileChanged.emit(self.__joint_profiles_names)

    def handle_delete_profile(self, profile_id):
        joint_profile = models.JoinProfile.objects.get(pk=profile_id)
        self.__joint_profiles_names.remove(joint_profile.profile_name)
        joint_profile.delete()
        row_index = self.get_row_id(profile_id)
        self.widget_table.removeRow(row_index)
        self.profileChanged.emit(self.__joint_profiles_names)




    def get_loaded_profiles(self):
        return self.__joint_profiles_names

    def change_measure_mode(self, unit: MeasureUnitType):
        pass

    def get_footer_btn_name(self) -> str:
        return self.__footer_btn_text

    def destroy_all_operations(self):
        pass

    def is_dirty(self) -> bool:
        pass

    def save_changes(self):
        pass

    def discard_changes(self):
        pass

    def new_image_received(self, camera_index, pix_map):
        pass



if __name__ == "__main__":
    from views import utils
    app = QtWidgets.QApplication([])
    utils.load_app_fonts()
    #
    joint_profile = JointProfilesPageManager("Joint Profile")
    app.setStyleSheet(utils.load_app_style())
    joint_profile.showMaximized()
    app.exec_()



