import os
try:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
except Exception as e:
    print(e)

from apps.sanding_machine import models
from PySide2 import QtWidgets, QtCore
from view_managers.utils import display_error_message
from custom_widgets.spin_box import CustomSpinBox
from configurations import machine_ranges
from configurations.settings import CURRENT_MACHINE
import django



class EditSanderDialog(QtWidgets.QDialog):
    def __init__(self, sander_id , parent=None):
        super(EditSanderDialog, self).__init__(parent=parent)
        self.widget_layout = QtWidgets.QGridLayout(self)
        self.current_sander = models.Sander.objects.get(pk=sander_id)
        # create UI
        self.x_length = CustomSpinBox(
            *machine_ranges.sander_x_length,
            initial_mm=self.current_sander.x_length,
            disp_precession=0,
            numpad_title="x length",
            allow_mode_change=True
        )
        self.widget_layout.addWidget(
            QtWidgets.QLabel("X Length"),
            0, 0, 1, 1
        )
        self.widget_layout.addWidget(
            self.x_length,
            0, 1, 1, 1
        )
        ##################################################
        self.y_length = CustomSpinBox(
            *machine_ranges.sander_y_length,
            initial_mm=self.current_sander.y_length,
            disp_precession=0,
            numpad_title="Y Length",
            allow_mode_change=True
        )
        self.widget_layout.addWidget(
            QtWidgets.QLabel("Y Length"),
            1, 0, 1, 1
        )
        self.widget_layout.addWidget(
            self.y_length,
            1, 1, 1, 1
        )
        ###########################################
        self.is_square_checkbox = QtWidgets.QCheckBox()
        self.is_square_checkbox.setChecked(self.current_sander.is_square)
        self.widget_layout.addWidget(
            QtWidgets.QLabel("Square"),
            2, 0, 1, 1
        )
        self.widget_layout.addWidget(
            self.is_square_checkbox,
            2, 1, 1, 1
        )
        ###########################################
        self.is_fine_checkbox = QtWidgets.QCheckBox()
        self.is_fine_checkbox.setChecked(self.current_sander.is_fine)
        self.widget_layout.addWidget(
            QtWidgets.QLabel("Fine"),
            3, 0, 1, 1
        )
        self.widget_layout.addWidget(
            self.is_fine_checkbox,
            3, 1, 1, 1
        )
        ###############################################
        self.installed_sandpaper_combo = QtWidgets.QComboBox()
        all_installed_paper_names = models.Sandpaper.get_sandpaper_names()
        self.installed_sandpaper_combo.addItems(all_installed_paper_names)
        current_sand_paper = "" if self.current_sander.installed_sandpaper is None else self.current_sander.installed_sandpaper.profile_name
        if current_sand_paper in all_installed_paper_names:
            self.installed_sandpaper_combo.setCurrentText(current_sand_paper)
        else:
            self.installed_sandpaper_combo.setCurrentIndex(-1)
        self.widget_layout.addWidget(
            QtWidgets.QLabel("Sandpaper"),
            4, 0, 1, 1
        )
        self.widget_layout.addWidget(
            self.installed_sandpaper_combo,
            4, 1, 1, 1
        )
        self.setWindowTitle(f"Edit {self.current_sander.name}")

        self.save_btn = QtWidgets.QPushButton("Update")
        self.save_btn.setFixedSize(150, 60)
        self.widget_layout.addWidget(
            self.save_btn,
            5, 1, 1, 1, alignment=QtCore.Qt.AlignRight
        )
        self.save_btn.clicked.connect(self.update_sander_prams)


    def update_sander_prams(self):
        installed_sandpaper_text = self.installed_sandpaper_combo.currentText()
        if len(installed_sandpaper_text) == 0:
            display_error_message("you have to configure the sandpaper first", "No sandpaper selected", self)
            return
        self.current_sander.x_length = self.x_length.value()
        self.current_sander.y_length = self.y_length.value()
        self.current_sander.is_square = self.is_square_checkbox.isChecked()
        self.current_sander.is_fine = self.is_fine_checkbox.isChecked()
        self.current_sander.installed_sandpaper = models.Sandpaper.objects.get(profile_name=installed_sandpaper_text)
        self.current_sander.save()
        self.accept()

    def get_current_objects(self):
        return self.current_sander

if __name__ == "__main__":
    from views import utils
    app = QtWidgets.QApplication([])
    utils.load_app_fonts()
    add_edit_dialog = EditSanderDialog(1)
    app.setStyleSheet(utils.load_app_style())
    add_edit_dialog.exec_()
    app.exec_()

