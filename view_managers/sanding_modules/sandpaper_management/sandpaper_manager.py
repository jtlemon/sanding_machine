import os
try:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
except Exception as e:
    print(e)
from apps.sanding_machine import models
from PySide2 import QtWidgets, QtCore
from view_managers.sanding_modules.sandpaper_management.individual_sandpaper_setting_dialog import  AddEditSandpaperProfileDialog
from configurations.constants_types import AppSupportedOperations
from view_managers.profiles_helper_functions import get_supported_profiles_meta
from view_managers.utils import add_item_to_table
from views.custom_app_widgets import RecordTrackBtn, CenterPagePushButton
from models.custom_app_types import MeasureUnitType
from configurations.common_configurations import CURRENT_MACHINE


class TableWithAddButtonWidgetView(QtWidgets.QGroupBox):
    def __init__(self, widget_title="", col_names = []):
        super(TableWithAddButtonWidgetView, self).__init__()
        self.setTitle(widget_title)
        self.widget_layout = QtWidgets.QVBoxLayout(self)
        # header
        self.header_layout = QtWidgets.QHBoxLayout()
        self.header_layout.addStretch(1)
        self.add_btn = CenterPagePushButton("Add")
        self.add_btn.widget_btn.setMinimumSize(300, 60)
        self.header_layout.addWidget(self.add_btn)
        self.header_layout.addStretch(1)
        self.widget_layout.addLayout(self.header_layout, stretch=0)
        self.widget_table = QtWidgets.QTableWidget()
        self.widget_table.setColumnCount(len(col_names))
        self.widget_table.setHorizontalHeaderLabels(col_names)
        for i in range(self.widget_table.columnCount() - 2):
            self.widget_table.horizontalHeader().setSectionResizeMode(i, QtWidgets.QHeaderView.Stretch)
        self.widget_layout.addWidget(self.widget_table)

    def get_row_id(self, item_pk):
        row_id = -1
        for row_index in range(self.widget_table.rowCount()):
            lst_btn = self.widget_table.cellWidget(row_index, self.widget_table.columnCount() - 1)
            if item_pk == lst_btn.get_id():
                row_id = row_index
        if row_id < 0:
            raise ValueError(f"the id field should be > 0 order pk {item_pk}")
        return row_id

    def handle_delete_profile(self, part_profile_id):
        part_profile = models.PartProfile.objects.get(pk=part_profile_id)
        part_profile.delete()
        row_index = self.get_row_id(part_profile_id)
        self.widget_table.removeRow(row_index)



class SandpaperWidget(TableWithAddButtonWidgetView):
    profileClicked = QtCore.Signal(int)
    profilesChanged = QtCore.Signal(set)
    def __init__(self):
        self.__all_loaded_profiles = set()
        col_names = ["Name"]
        names, self.target_db_keys, self.default_values = get_supported_profiles_meta(
            AppSupportedOperations.individualSandPaperOperations)
        col_names.extend(names)
        col_names.extend(["#", "#"])
        super(SandpaperWidget, self).__init__(widget_title="sandpaper", col_names=col_names)
        self.add_btn.clicked.connect(self.handle_add_new_part)
        self.reload_profiles_table()

    def handle_delete_profile(self, part_profile_id):
        profile_name = super(SandpaperWidget, self).handle_delete_profile(part_profile_id)
        self.__all_loaded_profiles.remove(profile_name)
        self.profilesChanged.emit(self.__all_loaded_profiles)

    def handle_add_new_part(self):
        dia = AddEditSandpaperProfileDialog(parent=self)
        if dia.exec_():
            part_profile = dia.get_profile()
            self.append_profile_to_table(part_profile)
            self.__all_loaded_profiles.add(part_profile.profile_name)
            self.profilesChanged.emit(self.__all_loaded_profiles)

    def handle_edit_profile(self, sandpaper_profile_id):
        sandpaper_profile = models.Sandpaper.objects.get(pk=sandpaper_profile_id)
        row_index = self.get_row_id(sandpaper_profile_id)
        old_profile_name = sandpaper_profile.profile_name
        dia = AddEditSandpaperProfileDialog(sandpaper_profile=sandpaper_profile, parent=self)
        if dia.exec_():
            sandpaper_profile = dia.get_profile()
            new_profile_name = sandpaper_profile.profile_name
            self.append_profile_to_table(sandpaper_profile , row_index=row_index)
            if new_profile_name != old_profile_name:
                self.__all_loaded_profiles.add(sandpaper_profile.profile_name)
                self.__all_loaded_profiles.remove(old_profile_name)
                self.profilesChanged.emit(self.__all_loaded_profiles)

    def reload_profiles_table(self):
        self.widget_table.setRowCount(0)
        self.__all_loaded_profiles = set()
        print(CURRENT_MACHINE)
        for part_profile in models.Sandpaper.objects.filter(machine=CURRENT_MACHINE):
            print(part_profile)
            self.append_profile_to_table(part_profile)
            self.__all_loaded_profiles.add(part_profile.profile_name)
        self.profilesChanged.emit(self.__all_loaded_profiles)

    def append_profile_to_table(self, sandpaper_profile, row_index=-1):
        has_to_update_model = False
        update_opt = True
        if row_index == -1:
            update_opt = False
            row_index = self.widget_table.rowCount()
            self.widget_table.insertRow(row_index)
        add_item_to_table(self.widget_table, row_index, 0, sandpaper_profile.profile_name)
        for col_index, key in enumerate(self.target_db_keys):
            value = sandpaper_profile.get_value(key)
            add_item_to_table(self.widget_table, row_index, col_index+1, value)

        if update_opt is False:
            edit_btn = RecordTrackBtn(sandpaper_profile.pk, ":/icons/icons/icons8-edit-96.png")
            del_btn = RecordTrackBtn(sandpaper_profile.pk, ":/icons/icons/icons8-delete-bin-96.png")
            self.widget_table.setCellWidget(row_index, col_index+2, edit_btn)
            self.widget_table.setCellWidget(row_index, col_index+3 , del_btn)
            edit_btn.customClickSignal.connect(self.handle_edit_profile)
            del_btn.customClickSignal.connect(self.handle_delete_profile)
            if has_to_update_model:
                sandpaper_profile.save()

    def get_loaded_profiles(self):
        return self.__all_loaded_profiles





class SandingProfilePageManager(QtWidgets.QWidget):
    profileClicked = QtCore.Signal(int)
    profilesChanged = QtCore.Signal(set)
    def __init__(self, footer_btn="Sandpaper"):
        super(SandingProfilePageManager, self).__init__()
        self.__footer_btn_text = footer_btn
        self.widget_layout = QtWidgets.QVBoxLayout(self)
        self.sandpaper_widget = SandpaperWidget()
        self.widget_layout.addWidget(self.sandpaper_widget)


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
    w = SandingProfilePageManager()
    w.show()
    app.setStyleSheet(utils.load_app_style())
    app.exec_()

