import os
try:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
except Exception as e:
    print(e)
from apps.sanding_machine import models
from PySide2 import QtWidgets, QtCore, QtGui
from models import MeasureUnitType
from view_managers.utils import add_item_to_table
from view_managers.sanding_modules.sander_management.add_edit_sander_dialog import EditSanderDialog


class SanderListingViewManagement(QtWidgets.QTableWidget):
    def __init__(self, footer_btn_text = "Sanders Management"):
        super(SanderListingViewManagement, self).__init__()
        self.__footer_btn_text = footer_btn_text
        col_names = (["Name", "X length", "Y length", "Square", "Fine", "Sandpaper", "#"])
        self.setColumnCount(len(col_names))
        self.setHorizontalHeaderLabels(col_names)
        for i in range(self.columnCount() - 1):
            self.horizontalHeader().setSectionResizeMode(i, QtWidgets.QHeaderView.Stretch)
        # load sanders
        all_sanders = models.Sander.objects.all()
        for sander in all_sanders:
            row_index = self.rowCount()
            self.insertRow(row_index)
            self.load_load_sander_information(row_index, sander)

    def load_load_sander_information(self, row_index, sander, update= False):
        add_item_to_table(self, row_index, 0, sander.name)
        add_item_to_table(self, row_index, 1, sander.x_length)
        add_item_to_table(self, row_index, 2, sander.y_length)
        add_item_to_table(self, row_index, 3, sander.is_square)
        add_item_to_table(self, row_index, 4, sander.is_fine)
        installed_sandpaper = "" if sander.installed_sandpaper is None else sander.installed_sandpaper.profile_name
        add_item_to_table(self, row_index, 5, installed_sandpaper)
        if update is False:
            edit_btn = QtWidgets.QPushButton()
            edit_btn.setIcon(QtGui.QIcon(":/icons/icons/icons8-edit-96.png"))
            edit_btn.setIconSize(QtCore.QSize(24, 24))
            edit_btn.clicked.connect(self.edit_sander_id_factory(sander.pk, row_index))
            self.setCellWidget(row_index, 6, edit_btn)

    def edit_sander_id_factory(self, sander_id, row_index):
        return  lambda : self.handle_sander_update(sander_id, row_index)

    def handle_sander_update(self, sander_id, row_index):
        dia = EditSanderDialog(sander_id, self)
        if dia.exec_():
            sander_obj = dia.get_current_object()
            self.load_load_sander_information(row_index, sander_obj, True)

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
    w = SanderListingViewManagement()
    w.show()
    app.setStyleSheet(utils.load_app_style())
    app.exec_()

