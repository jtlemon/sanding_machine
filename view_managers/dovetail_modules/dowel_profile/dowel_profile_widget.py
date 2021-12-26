import os
try:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
except Exception as e:
    print(e)
from apps.dowel_profiles import models
from PySide2 import QtWidgets, QtCore
from view_managers.dovetail_modules.dowel_profile.add_edit_dowel_profile_dialog import  AddEditDowelProfileDialog
from configurations.constants_types import AppSupportedOperations
from view_managers.profiles_helper_functions import get_supported_profiles_meta
from view_managers.utils import add_item_to_table
from views.custom_app_widgets import RecordTrackBtn, CenterPagePushButton
from configurations.common_configurations import CURRENT_MACHINE

class ProfileListWidget(QtWidgets.QWidget):
    profileClicked = QtCore.Signal(int)
    profilesChanged = QtCore.Signal(set)
    def __init__(self):
        super(ProfileListWidget, self).__init__()
        self.__current_dowel_profile = None
        self.__all_loaded_profiles = set()
        self.widget_layout = QtWidgets.QVBoxLayout(self)
        self.add_dowel_profile_btn = CenterPagePushButton("Add New Profile")
        self.add_dowel_profile_btn.widget_btn.setMinimumSize(300, 60)
        self.widget_layout.addWidget(self.add_dowel_profile_btn)
        # table widget
        col_names = ["Name"]
        names, self.target_db_keys, self.default_values = get_supported_profiles_meta(AppSupportedOperations.dowelsProfileOperation)
        col_names.extend(names)
        col_names.extend(["Bit", "#", "#"])
        self.widget_table = QtWidgets.QTableWidget()
        self.widget_table.setColumnCount(len(col_names))
        self.widget_table.setHorizontalHeaderLabels(col_names)
        for i in range(self.widget_table.columnCount() - 2):
            self.widget_table.horizontalHeader().setSectionResizeMode(i, QtWidgets.QHeaderView.Stretch)
        self.widget_layout.addWidget(self.widget_table, stretch=1)
        # signals
        self.widget_table.cellDoubleClicked.connect(self.filter_table_cell_clicked)
        self.add_dowel_profile_btn.clicked.connect(self.handle_add_new_dowel)
        self.reload_profiles_table()



    def reload_profiles_table(self):
        self.widget_table.setRowCount(0)
        self.__all_loaded_profiles = set()
        for dowel_profile in models.DowelProfile.objects.filter(machine= CURRENT_MACHINE):
            self.append_profile_to_table(dowel_profile)
            self.__all_loaded_profiles.add(dowel_profile.profile_name)
        self.profilesChanged.emit(self.__all_loaded_profiles)


    def append_profile_to_table(self, dowel_profile, row_index=-1):
        has_to_update_model = False
        update_opt = True
        if row_index == -1:
            update_opt = False
            row_index = self.widget_table.rowCount()
            self.widget_table.insertRow(row_index)
        add_item_to_table(self.widget_table, row_index, 0, dowel_profile.profile_name)
        for col_index, key in enumerate(self.target_db_keys):
            default_value = self.default_values[col_index]
            value = dowel_profile.get_value(key)
            if value is None:
                has_to_update_model = True
                value = default_value
                dowel_profile.set_value(key, value)
            add_item_to_table(self.widget_table, row_index, col_index+1, value)
        col_index = col_index + 2
        add_item_to_table(self.widget_table, row_index, col_index, dowel_profile.bit_profile.profile_name)
        if update_opt is False:
            edit_btn = RecordTrackBtn(dowel_profile.pk, ":/icons/icons/icons8-edit-96.png")
            del_btn = RecordTrackBtn(dowel_profile.pk, ":/icons/icons/icons8-delete-bin-96.png")
            self.widget_table.setCellWidget(row_index, col_index+1, edit_btn)
            self.widget_table.setCellWidget(row_index, col_index+2 , del_btn)
            edit_btn.customClickSignal.connect(self.handle_edit_profile)
            del_btn.customClickSignal.connect(self.handle_delete_profile)
            if has_to_update_model:
                dowel_profile.save()

    def handle_delete_profile(self, dowel_profile_id):
        dowel_profile = models.DowelProfile.objects.get(pk=dowel_profile_id)
        self.__all_loaded_profiles.add(dowel_profile.profile_name)
        dowel_profile.delete()
        self.profilesChanged.emit(self.__all_loaded_profiles)
        row_index = self.get_row_id(dowel_profile_id)
        self.widget_table.removeRow(row_index)

    def handle_edit_profile(self, dowel_profile_id):
        dowel_profile = models.DowelProfile.objects.get(pk=dowel_profile_id)
        row_index = self.get_row_id(dowel_profile_id)
        old_profile_name = dowel_profile.profile_name
        dia = AddEditDowelProfileDialog(dowel_profile=dowel_profile, parent=self)
        if dia.exec_():
            dowel_profile = dia.get_profile()
            new_profile_name = dowel_profile.profile_name
            self.append_profile_to_table(dowel_profile , row_index=row_index)
            if new_profile_name != old_profile_name:
                self.__all_loaded_profiles.add(dowel_profile.new_profile_name)
                self.__all_loaded_profiles.remove(old_profile_name)
                self.profilesChanged.emit(self.__all_loaded_profiles)

    def get_loaded_profiles(self):
        return self.__all_loaded_profiles

    def handle_add_new_dowel(self):
        dia = AddEditDowelProfileDialog(parent=self)
        if dia.exec_():
            dowel_profile = dia.get_profile()
            self.append_profile_to_table(dowel_profile)
            self.__all_loaded_profiles.add(dowel_profile.profile_name)
            self.profilesChanged.emit(self.__all_loaded_profiles)

    def get_row_id(self, item_pk):
        row_id = -1
        for row_index in range(self.widget_table.rowCount()):
            lst_btn = self.widget_table.cellWidget(row_index, self.widget_table.columnCount() - 1)
            if item_pk == lst_btn.get_id():
                row_id = row_index
        if row_id < 0:
            raise ValueError(f"the id field should be > 0 order pk {item_pk}")
        return row_id

    def filter_table_cell_clicked(self, row_index, col_index):
        if col_index == 0:
            lst_btn = self.widget_table.cellWidget(row_index, self.widget_table.columnCount() - 1)
            dowel_profile_id = lst_btn.get_id()
            self.profileClicked.emit(dowel_profile_id)



if __name__ == "__main__":
    from views import utils
    app = QtWidgets.QApplication([])
    w = ProfileListWidget()
    w.show()
    app.setStyleSheet(utils.load_app_style())
    app.exec_()

