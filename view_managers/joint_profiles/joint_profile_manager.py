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
from view_managers.utils import add_item_to_table
from views.custom_app_widgets import RecordTrackBtn





class JointProfilesPageManager(QtWidgets.QWidget):
    profileChanged = QtCore.Signal(set)
    def __init__(self, footer_btn=""):
        super(JointProfilesPageManager, self).__init__()
        self.__joint_profiles_names = set()
        self.__footer_btn_text = "Joint Profiles" if len(footer_btn) == 0 else footer_btn
        if static_configurations.CURRENT_MACHINE == static_configurations.SupportedMachines.dovetailMachine:
             supported_joint_profiles = static_configurations.DOVETAIL_JOINT_PROFILE_CONFIGURATION
        else:
            raise ValueError("not supported machine.......")
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
        for joint_config in supported_joint_profiles:
            widget_range = joint_config.get("range")
            lbl_text = joint_config.get("lbl")
            target_key = joint_config.get("target_key")
            col_names.append(lbl_text)
            self.target_db_keys.append(target_key)
            self.default_values.append(widget_range[0])
        col_names.extend(["Bit" ,"#" , "#"])
        self.widget_table = QtWidgets.QTableWidget()
        self.widget_table.setColumnCount(len(col_names))
        self.widget_table.setHorizontalHeaderLabels(col_names)
        for i in range(self.widget_table.columnCount()-2):
            self.widget_table.horizontalHeader().setSectionResizeMode(i, QtWidgets.QHeaderView.Stretch)
        self.widget_layout.addWidget(self.widget_table, stretch=1)
        self.add_profile_btn.clicked.connect(self.handle_add_profile)
        self.reload_joint_profiles()

    def reload_joint_profiles(self):
        # clear table
        self.widget_table.setRowCount(0)
        self.__joint_profiles_names = set()
        for joint_profile in models.JoinProfile.objects.filter(machine=static_configurations.CURRENT_MACHINE):
            self.append_joint_to_table(joint_profile)
            self.__joint_profiles_names.add(joint_profile.profile_name)
        self.profileChanged.emit(self.__joint_profiles_names)

    def append_joint_to_table(self, joint_profile, row_index=-1):
        has_to_update_model = False
        update_opt = True
        if row_index == -1:
            update_opt = False
            row_index = self.widget_table.rowCount()
            self.widget_table.insertRow(row_index)
        add_item_to_table(self.widget_table, row_index, 0, joint_profile.profile_name)
        for col_index, key in enumerate(self.target_db_keys):
            default_value = self.default_values[col_index]
            value = joint_profile.get_value(key)
            if value is None:
                has_to_update_model = True
                value = default_value
                joint_profile.set_value(key, value)
            add_item_to_table(self.widget_table, row_index, col_index+1, value)
        col_index = col_index + 2
        add_item_to_table(self.widget_table, row_index, col_index, joint_profile.bit_profile.profile_name)
        if update_opt is False:
            edit_btn = RecordTrackBtn(joint_profile.pk, ":/icons/icons/icons8-edit-96.png")
            del_btn = RecordTrackBtn(joint_profile.pk, ":/icons/icons/icons8-delete-bin-96.png")
            self.widget_table.setCellWidget(row_index, col_index+1, edit_btn)
            self.widget_table.setCellWidget(row_index, col_index+2, del_btn)
            edit_btn.customClickSignal.connect(self.handle_edit_profile)
            del_btn.customClickSignal.connect(self.handle_delete_profile)
            if has_to_update_model:
                joint_profile.save()

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


    def get_row_id(self, item_pk):
        row_id = -1
        for row_index in range(self.widget_table.rowCount()):
            lst_btn = self.widget_table.cellWidget(row_index, self.widget_table.columnCount() - 1)
            if item_pk == lst_btn.get_id():
                row_id = row_index
        if row_id < 0:
            raise ValueError(f"the id field should be > 0 order pk {item_pk}")
        return row_id

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
