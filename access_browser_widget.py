import os
from pathlib import Path
from typing import  List, Dict, Union
try:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    from django.core.wsgi import get_wsgi_application

    application = get_wsgi_application()
except Exception as e:
    print(e)


import jaydebeapi
from models.draw_utils import draw_parts_on_image
from models.access_db_parser import MDBFileConnector
from PySide2 import QtCore, QtGui, QtWidgets
import numpy as np
import cv2
from views.generated.access_viewer_widget import Ui_AccessViewerWidget


class CustomIdButton(QtWidgets.QPushButton):
    showSignal = QtCore.Signal(int)
    def __init__(self,btn_id, *args, **kwargs):
        super(CustomIdButton, self).__init__(*args, **kwargs)
        self.clicked.connect(lambda :self.showSignal.emit(btn_id))

class ImageViewerDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Image Viewer")
        self.image_label = QtWidgets.QLabel()
        self.image_label.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        self.image_label.setScaledContents(True)
        self.image_label.setFixedSize(800, 600)
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setBackgroundRole(QtGui.QPalette.Dark)
        self.scroll_area.setWidget(self.image_label)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addWidget(self.scroll_area)
        self.setLayout(self.main_layout)
        self.setMinimumSize(840, 640)
        self.adjustSize()

    def set_image(self, image: QtGui.QImage):
        self.image_label.setPixmap(QtGui.QPixmap.fromImage(image))

    def set_image_path(self, image_path: Path):
        image = QtGui.QImage(str(image_path))
        self.set_image(image)

    def draw_part(self, parts):
        height, width =  self.image_label.size().height() , self.image_label.size().width()
        image = np.zeros((width, height, 3), dtype=np.uint8)
        image.fill(255)
        image = draw_parts_on_image(image, parts)
        cv2.imwrite("test.png", image)
        self.set_image_path(Path("test.png"))


class AccessBrowserWidget(QtWidgets.QWidget, Ui_AccessViewerWidget):
    def __init__(self):
        super(AccessBrowserWidget, self).__init__()
        self._mdb_file_connector = None
        self._current_table_name = ""
        self.setupUi(self)
        self._install_signals()

    def _install_signals(self):
        self.browse_btn.clicked.connect(self._browse_btn_clicked)
        self.table_names_list_widget.itemClicked.connect(self._table_name_clicked)

    def _browse_btn_clicked(self):
        file_path = QtWidgets.QFileDialog.getOpenFileName(self, "Open Access File", "", "Access Files (*.tld)")
        if file_path[0]:
            self.file_path_le.setText(file_path[0])
            #self._load_file(file_path[0])
            self._mdb_file_connector = MDBFileConnector(Path(file_path[0]))
            table_names = self._mdb_file_connector.list_tables()
            self._load_table_names(table_names)

    def _load_table_names(self, table_names: List[str]):
        self.table_names_list_widget.clear()
        self.table_names_list_widget.addItems(table_names)
        self.table_names_list_widget.setCurrentRow(0)
        self._table_name_clicked(self.table_names_list_widget.currentItem())

    def _table_name_clicked(self, item: QtWidgets.QListWidgetItem):
        self._load_table_content(item.text())

    def _load_table_content(self, table_name: str):
        self._current_table_name = table_name
        self.tableWidget.clear()
        self.tableWidget.setRowCount(0)
        columns = self._mdb_file_connector.get_table_columns(table_name)
        if self._current_table_name == "Parts":
            self.tableWidget.setColumnCount(len(columns)+1)
        else:
            self.tableWidget.setColumnCount(len(columns))
        self.tableWidget.setHorizontalHeaderLabels(columns)
        table_content = self._mdb_file_connector.get_table_content(table_name)
        for row in table_content:
            values = [str(row[key]) for key in columns]
            if self._current_table_name == "Parts":
                values = [""] + values
            self.add_row_to_table(values)

    def add_row_to_table(self, row: List[str]):
        row_position = self.tableWidget.rowCount()
        self.tableWidget.insertRow(row_position)
        for column, item in enumerate(row):
            if self._current_table_name == "Parts" and column == 0:
                btn = CustomIdButton(int(row[1]), "Show")
                btn.showSignal.connect(self._show_part_image)
                self.tableWidget.setCellWidget(row_position, column, btn)
            else:
                self.tableWidget.setItem(row_position, column, QtWidgets.QTableWidgetItem(item))

    def _show_part_image(self, part_id:int):
        parts = self._mdb_file_connector.get_parts(part_id)
        dia = ImageViewerDialog(self)
        dia.draw_part(parts)
        dia.exec_()

    def change_measure_mode(self, unit):
        pass

    def get_footer_btn_name(self) -> str:
        return "Access Viewer"

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
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = AccessBrowserWidget()
    window.show()
    sys.exit(app.exec_())