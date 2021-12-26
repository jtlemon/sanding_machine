import os

try:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    from django.core.wsgi import get_wsgi_application

    application = get_wsgi_application()
except Exception as e:
    print(e)

from apps.sanding_machine import models
from PySide2 import QtWidgets, QtCore
from views.sanding_program_dialog import SandingProgramCreationDialog
from view_managers.utils import display_error_message


class AddEditSandingProgramDialog(SandingProgramCreationDialog):
    def __init__(self, sanding_program: models.SandingProgram = None, parent=None):
        super(AddEditSandingProgramDialog, self).__init__(parent=parent)
        # init ui
        self.sanders_combo_box.addItems(["Sander1", "Sander2", "Sander3", "Sander4"])
        self.sanders_combo_box.setCurrentIndex(-1)
        self.passes_list.clear()

        self.passes_count = 0
        self.__all_added_passes = list()
        self.__current_sanding_program = sanding_program
        self.__current_sanding_program_name = "" if sanding_program is None else sanding_program.name
        self.__current_sanding_pass = None
        self.__current_sanding_pass_index = -1
        if self.__current_sanding_program is None:
            self.setWindowTitle("Create new program")
            self.stackedWidget.setCurrentIndex(0)
        else:
            self.setWindowTitle(f"update program {sanding_program.name}")
            self.load_program_details()

        # install signals
        self.sanders_combo_box.currentTextChanged.connect(self.__handle_sander_changed)
        self.add_pass_btn.clicked.connect(self._handle_add_new_pass)
        self.passes_list.itemClicked.connect(self._handle_pass_clicked)
        self.panels_checkbox.toggled.connect(lambda new_state: self.panel_option_frame.setVisible(new_state))
        self.save_update_btn.clicked.connect(self.save_program)

    def __handle_sander_changed(self, sander_name):
        if len(sander_name) > 0 and self.__current_sanding_pass.is_temp:
            sander = models.Sander.objects.get(name=sander_name)
            installed_sandpaper = sander.installed_sandpaper
            self.set_spinbox_value(self.overlap_spinbox, installed_sandpaper.get_value("sandpaper_overlap"))
            self.set_spinbox_value(self.pressure_spinbox, installed_sandpaper.get_value("sanding_pressure"))
            self.set_spinbox_value(self.speed_spinbox, installed_sandpaper.get_value("sandpaper_speed"))
            self.set_spinbox_value(self.hangover_spinbox, installed_sandpaper.get_value("sandpaper_overhang"))

    def _handle_pass_clicked(self, item: QtWidgets.QListWidgetItem):
        item_index = self.passes_list.row(item)
        if self.__current_sanding_pass is not None:
            is_created = self.create_pass()
            if not is_created:
                self.passes_list.setCurrentRow(self.__current_sanding_pass_index)
                return
        self._load_pass_at_index(item_index)

    def _load_pass_at_index(self, pass_index: int):
        self.passes_list.setCurrentRow(pass_index)
        self.__current_sanding_pass_index = pass_index
        self.__current_sanding_pass = self.__all_added_passes[pass_index]
        self.load_pass_details(self.__all_added_passes[pass_index])

    def _handle_add_new_pass(self):
        if self.__current_sanding_pass is not None and self.create_pass() is False:
            return
        self.passes_count += 1
        pass_name = f"pass {self.passes_count}"
        self.passes_list.addItem(QtWidgets.QListWidgetItem(pass_name))
        new_pass_obj = models.SandingProgramPass()
        new_pass_obj.save()
        self.__all_added_passes.append(new_pass_obj)
        self._load_pass_at_index(self.passes_count - 1)

    def load_program_details(self):
        self.program_name_lin.setText(self.__current_sanding_program.name)
        # get all passes
        available_passes = models.SandingProgramPass.objects.filter(
            sanding_program=self.__current_sanding_program,
            is_temp=False
        )
        for index, sanding_program_pass in enumerate(available_passes):
            self.passes_count += 1
            pass_name = f"pass {self.passes_count}"
            self.passes_list.addItem(QtWidgets.QListWidgetItem(pass_name))
            self.__all_added_passes.append(sanding_program_pass)
        if self.passes_count > 0:
            self._load_pass_at_index(0)

    def load_pass_details(self, sanding_program_pass: models.SandingProgramPass):
        # make sure the configuration content is visible
        self.stackedWidget.setCurrentIndex(1)
        if sanding_program_pass.sander is None:
            self.sanders_combo_box.setCurrentIndex(-1)
        else:
            self.sanders_combo_box.setCurrentText(sanding_program_pass.sander.name)
        self.frames_checkbox.setChecked(sanding_program_pass.contain_frames)
        self.panels_checkbox.setChecked(sanding_program_pass.contain_panels)
        if sanding_program_pass.contain_panels:
            self.panel_option_frame.setVisible(True)
        else:
            self.panel_option_frame.setVisible(False)
        if sanding_program_pass.is_entire_panel is None:
            self.entrire_panel_radio.setChecked(False)
            self.only_perimeter_radio.setChecked(False)
        else:
            self.entrire_panel_radio.setChecked(sanding_program_pass.is_entire_panel)
            self.only_perimeter_radio.setChecked(not sanding_program_pass.is_entire_panel)
        self.slabs_checkbox.setChecked(sanding_program_pass.contain_slabs)
        self.extra_pass_around_perimeter_checkbox.setChecked(sanding_program_pass.make_extra_pass_around_perimeter)

        self.set_spinbox_value(self.overlap_spinbox, sanding_program_pass.overlap_value)
        self.set_spinbox_value(self.pressure_spinbox, sanding_program_pass.pressure_value)
        self.set_spinbox_value(self.speed_spinbox, sanding_program_pass.speed_value)
        self.set_spinbox_value(self.hangover_spinbox, sanding_program_pass.hangover_value)

    @staticmethod
    def set_spinbox_value(spinbox, value):
        if value is not None:
            spinbox.set_value_and_reset_state(value)
        else:
            spinbox.set_min_limit()


    def create_pass(self):
        sander_name = self.sanders_combo_box.currentText()
        if len(sander_name) == 0:
            display_error_message("please select sander first.", "select sander", self)
            return False
        self.__current_sanding_pass.sanding_program = self.__current_sanding_program
        self.__current_sanding_pass.sander = models.Sander.objects.get(name=sander_name)
        self.__current_sanding_pass.contain_frames = self.frames_checkbox.isChecked()
        is_panel_checked = self.panels_checkbox.isChecked()
        self.__current_sanding_pass.contain_panels = is_panel_checked
        if is_panel_checked:
            if self.entrire_panel_radio.isChecked() is False and self.only_perimeter_radio.isChecked() is False:
                display_error_message("please select panel type first.", "panel type", self)
                return False
            self.__current_sanding_pass.is_entire_panel = self.entrire_panel_radio.isChecked()
        else:
            self.__current_sanding_pass.is_entire_panel = None
        self.__current_sanding_pass.contain_slabs = self.slabs_checkbox.isChecked()
        self.__current_sanding_pass.make_extra_pass_around_perimeter = self.extra_pass_around_perimeter_checkbox.isChecked()
        self.__current_sanding_pass.overlap_value = self.overlap_spinbox.value()
        self.__current_sanding_pass.pressure_value = self.pressure_spinbox.value()
        self.__current_sanding_pass.speed_value = self.speed_spinbox.value()
        self.__current_sanding_pass.hangover_value = self.hangover_spinbox.value()
        self.__current_sanding_pass.is_temp = False
        return True

    def save_program(self):
        if len(self.__all_added_passes) == 0:
            display_error_message(f"you have to add passes to the program first",
                                  "Program passes error", self)
            return
        # store the current pass first
        if not self.create_pass():
            return
        program_name = self.program_name_lin.text().strip()
        if len(program_name) == 0:
            display_error_message(f"please select program name first.",
                                  "Program name error", self)
            self.program_name_lin.setFocus()
            return
        if self.__current_sanding_program is None:
            self.__current_sanding_program = models.SandingProgram()
        if self.is_program_name_is_exist(program_name):
            display_error_message(f"{program_name} program is already exist please select another name.",
                                  "Program name error", self)
            self.program_name_lin.setFocus()
            return
        self.__current_sanding_program.name = program_name
        self.__current_sanding_program.save()
        self.__current_sanding_program_name = program_name
        for sanding_program_pass in self.__all_added_passes:
            sanding_program_pass.sanding_program = self.__current_sanding_program
            sanding_program_pass.is_temp = False
            sanding_program_pass.save()
        self.accept()

    def is_program_name_is_exist(self, program_name):
        return models.SandingProgram.objects.filter(name=program_name).exclude(
            name=self.__current_sanding_program_name).exists()

    def get_current_program(self):
        return self.__current_sanding_program


if __name__ == "__main__":
    from views import utils

    app = QtWidgets.QApplication([])
    utils.load_app_fonts()
    last_program = models.SandingProgram.objects.last()
    sanding_program_dialog = AddEditSandingProgramDialog(last_program)
    app.setStyleSheet(utils.load_app_style())
    sanding_program_dialog.exec_()
