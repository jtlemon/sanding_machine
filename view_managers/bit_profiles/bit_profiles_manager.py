import os

try:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    from django.core.wsgi import get_wsgi_application

    application = get_wsgi_application()
except Exception as e:
    print(e)
from apps.bit_profiles import models
from PySide2 import QtWidgets, QtCore, QtGui
import configurations.static_app_configurations as static_configurations
from view_managers.profiles_helper_functions import get_supported_profiles_meta
from view_managers.utils import add_item_to_table
from view_managers.bit_profiles.add_edit_bit_dialog import AddEditBitProfileDialog
from views.custom_app_widgets import RecordTrackBtn, CenterPagePushButton
from configurations.constants_types import AppSupportedOperations


class BitProfileManager(QtWidgets.QWidget):
    profileClicked = QtCore.Signal(int)
    def __init__(self, footer_btn=""):
        super(BitProfileManager, self).__init__()
        self.__footer_btn_text = "Bit Profiles" if len(footer_btn) == 0 else footer_btn
        self.widget_layout = QtWidgets.QVBoxLayout(self)
        self.add_dowel_profile_btn = CenterPagePushButton("Add New Profile")
        self.add_dowel_profile_btn.widget_btn.setMinimumSize(300, 60)
        self.widget_layout.addWidget(self.add_dowel_profile_btn)
        # table widget
        col_names = ["Name"]
        names, self.target_db_keys, self.default_values = get_supported_profiles_meta(AppSupportedOperations.bitProfilesOperation)
        col_names.extend(names)
        col_names.extend(["#", "#"])
        self.widget_table = QtWidgets.QTableWidget()
        self.widget_table.setColumnCount(len(col_names))
        self.widget_table.setHorizontalHeaderLabels(col_names)
        for i in range(self.widget_table.columnCount() - 2):
            self.widget_table.horizontalHeader().setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeToContents)
        self.widget_layout.addWidget(self.widget_table, stretch=1)
        self.add_dowel_profile_btn.clicked.connect(self.handle_add_new_dowel)
        self.reload_profiles_table()

    def get_footer_btn_name(self) -> str:
        return self.__footer_btn_text

    def reload_profiles_table(self):
        self.widget_table.setRowCount(0)
        for bit_profile in models.BitProfile.objects.filter(machine=static_configurations.CURRENT_MACHINE):
            self.append_profile_to_table(bit_profile)

    def append_profile_to_table(self, bit_profile, row_index=-1):
        has_to_update_model = False
        update_opt = True
        if row_index == -1:
            update_opt = False
            row_index = self.widget_table.rowCount()
            self.widget_table.insertRow(row_index)
        add_item_to_table(self.widget_table, row_index, 0, bit_profile.profile_name)
        for col_index, key in enumerate(self.target_db_keys):
            default_value = self.default_values[col_index]
            value = bit_profile.get_value(key)
            if value is None:
                has_to_update_model = True
                value = default_value
                bit_profile.set_value(key, value)
            add_item_to_table(self.widget_table, row_index, col_index + 1, value)
        if update_opt is False:
            edit_btn = RecordTrackBtn(bit_profile.pk, ":/icons/icons/icons8-edit-96.png")
            del_btn = RecordTrackBtn(bit_profile.pk, ":/icons/icons/icons8-delete-bin-96.png")
            col_index = col_index + 2
            self.widget_table.setCellWidget(row_index, col_index, edit_btn)
            self.widget_table.setCellWidget(row_index, col_index + 1, del_btn)
            edit_btn.customClickSignal.connect(self.handle_edit_profile)
            del_btn.customClickSignal.connect(self.handle_delete_profile)
            if has_to_update_model:
                bit_profile.save()

    def handle_delete_profile(self, dowel_profile_id):
        dowel_profile = models.BitProfile.objects.get(pk=dowel_profile_id)
        dowel_profile.delete()
        row_index = self.get_row_id(dowel_profile_id)
        self.widget_table.removeRow(row_index)

    def handle_edit_profile(self, dowel_profile_id):
        dowel_profile = models.BitProfile.objects.get(pk=dowel_profile_id)
        row_index = self.get_row_id(dowel_profile_id)
        dia = AddEditBitProfileDialog(dowel_profile, parent=self)
        if dia.exec_():
            self.append_profile_to_table(dia.get_profile(), row_index=row_index)

    def handle_add_new_dowel(self):
        dia = AddEditBitProfileDialog(parent=self)
        if dia.exec_():
            self.append_profile_to_table(dia.get_profile())

    def get_row_id(self, item_pk):
        row_id = -1
        for row_index in range(self.widget_table.rowCount()):
            lst_btn = self.widget_table.cellWidget(row_index, self.widget_table.columnCount() - 1)
            if item_pk == lst_btn.get_id():
                row_id = row_index
        if row_id < 0:
            raise ValueError(f"the id field should be > 0 order pk {item_pk}")
        return row_id


if __name__ == "__main__":
    from views import utils

    app = QtWidgets.QApplication([])
    w = BitProfileManager()
    w.show()
    app.setStyleSheet(utils.load_app_style())
    app.exec_()

