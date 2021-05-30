import os

try:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    from django.core.wsgi import get_wsgi_application

    application = get_wsgi_application()
except Exception as e:
    print(e)
from apps.dowel_profiles import models
from PySide2 import QtWidgets, QtCore
from view_managers.profiles_helper_functions import get_supported_profiles_meta
from view_managers.dowel_profile.add_edit_dowel_dialog import AddEditDowelDialog
from view_managers.utils import add_item_to_table
from configurations.constants_types import AppSupportedOperations
from views.custom_app_widgets import RecordTrackBtn, CenterPagePushButton


class DowelListWidget(QtWidgets.QWidget):
    backSignal = QtCore.Signal()

    def __init__(self):
        super(DowelListWidget, self).__init__()
        self.__current_dowel_profile = None
        self.widget_layout = QtWidgets.QVBoxLayout(self)
        self.profile_name_lbl = QtWidgets.QLabel()
        self.profile_name_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.widget_layout.addWidget(self.profile_name_lbl)
        self.add_dowel_btn = CenterPagePushButton("Add New Dowel")
        self.add_dowel_btn.widget_btn.setMinimumSize(300, 60)
        self.widget_layout.addWidget(self.add_dowel_btn)
        # table widget
        col_names, self.target_db_keys, self.default_values = get_supported_profiles_meta(AppSupportedOperations.dowelsProfileOperation)
        col_names.extend(["#", "#"])
        self.widget_table = QtWidgets.QTableWidget()
        self.widget_table.setColumnCount(len(col_names))
        self.widget_table.setHorizontalHeaderLabels(col_names)
        for i in range(self.widget_table.columnCount() - 2):
            self.widget_table.horizontalHeader().setSectionResizeMode(i, QtWidgets.QHeaderView.Stretch)
        self.widget_layout.addWidget(self.widget_table, stretch=1)
        # back btn
        self.back_btn = CenterPagePushButton("Back")
        self.back_btn.widget_btn.setMinimumSize(200, 60)
        self.widget_layout.addWidget(self.back_btn)
        # signals
        self.add_dowel_btn.clicked.connect(self.handle_add_new_dowel)
        self.back_btn.clicked.connect(lambda: self.backSignal.emit())

    def load_dowels(self, profile):
        self.profile_name_lbl.setText(profile.profile_name)
        self.__current_dowel_profile = profile
        self.widget_table.setRowCount(0)
        for dowel_joint in models.DowelJoint.objects.filter(profile=profile):
            self.append_joint_to_table(dowel_joint)

    def append_joint_to_table(self, dowel_joint, row_index=-1):
        has_to_update_model = False
        update_opt = True
        if row_index == -1:
            update_opt = False
            row_index = self.widget_table.rowCount()
            self.widget_table.insertRow(row_index)
        for col_index, key in enumerate(self.target_db_keys):
            default_value = self.default_values[col_index]
            value = dowel_joint.get_value(key)
            if value is None:
                has_to_update_model = True
                value = default_value
                dowel_joint.set_value(key, value)
            add_item_to_table(self.widget_table, row_index, col_index, value)
        if update_opt is False:
            edit_btn = RecordTrackBtn(dowel_joint.pk, ":/icons/icons/icons8-edit-96.png")
            del_btn = RecordTrackBtn(dowel_joint.pk, ":/icons/icons/icons8-delete-bin-96.png")
            col_index = col_index + 1
            self.widget_table.setCellWidget(row_index, col_index, edit_btn)
            self.widget_table.setCellWidget(row_index, col_index + 1, del_btn)
            edit_btn.customClickSignal.connect(self.handle_edit_dowel_joint)
            del_btn.customClickSignal.connect(self.handle_delete_dowel_joint)
            if has_to_update_model:
                dowel_joint.save()

    def handle_delete_dowel_joint(self, dowel_joint_id):
        dowel_joint = models.DowelJoint.objects.get(pk=dowel_joint_id)
        dowel_joint.delete()
        row_index = self.get_row_id(dowel_joint_id)
        self.widget_table.removeRow(row_index)

    def handle_edit_dowel_joint(self, dowel_joint_id):
        dowel_joint = models.DowelJoint.objects.get(pk=dowel_joint_id)
        row_index = self.get_row_id(dowel_joint_id)
        dia = AddEditDowelDialog(dowel_profile=self.__current_dowel_profile, dowel=dowel_joint, parent=self)
        if dia.exec_():
            self.append_joint_to_table(dia.get_dowel(), row_index=row_index)

    def handle_add_new_dowel(self):
        dia = AddEditDowelDialog(dowel_profile=self.__current_dowel_profile, parent=self)
        if dia.exec_():
            self.append_joint_to_table(dia.get_dowel())

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
    w = DowelListWidget()
    last_profile = models.DowelProfile.objects.last()
    w.load_dowels(last_profile)
    w.show()
    app.setStyleSheet(utils.load_app_style())
    app.exec_()
