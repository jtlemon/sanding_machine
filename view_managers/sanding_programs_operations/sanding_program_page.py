import os

try:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    from django.core.wsgi import get_wsgi_application

    application = get_wsgi_application()
except Exception as e:
    print(e)

from apps.sanding_machine import models

from PySide2 import QtWidgets, QtCore

from view_managers.abs_operation_widget_manager import AbstractOperationWidgetManger
from models.custom_app_types import MeasureUnitType
from view_managers.utils import add_item_to_table
from views.custom_app_widgets import RecordTrackBtn
from view_managers.sanding_programs_operations.add_edit_program_dialog import AddEditSandingProgramDialog


class SandingProgramsPageManager(QtWidgets.QWidget, AbstractOperationWidgetManger):
    programsChanged = QtCore.Signal(set)
    def __init__(self, footer_btn = "Sanding Programs"):
        super(SandingProgramsPageManager, self).__init__()
        self.__footer_btn_text = footer_btn
        self.widget_layout = QtWidgets.QVBoxLayout(self)
        self.__all_added_programs = set()
        # create dynamic widgets
        self.add_new_program_btn = QtWidgets.QPushButton("Add New Program")
        self.add_new_program_btn.setFixedSize(400, 60)
        self.widget_layout.addWidget(self.add_new_program_btn, alignment=QtCore.Qt.AlignCenter)
        col_names = ["Program Name", "No Of Passes", "#", "#"]
        self.widget_table = QtWidgets.QTableWidget()
        self.widget_table.setColumnCount(len(col_names))
        self.widget_table.setHorizontalHeaderLabels(col_names)
        for i in range(self.widget_table.columnCount() - 2):
            self.widget_table.horizontalHeader().setSectionResizeMode(i, QtWidgets.QHeaderView.Stretch)
        self.widget_layout.addWidget(self.widget_table, stretch=1)
        self.add_new_program_btn.clicked.connect(self.create_new_program)
        self.reload_all_programs()


    def reload_all_programs(self):
        for sanding_program in models.SandingProgram.objects.all():
            self.append_new_sanding_program(sanding_program, True)
            self.__all_added_programs.add(sanding_program.name)
        self.programsChanged.emit(self.__all_added_programs)

    def append_new_sanding_program(self, sanding_program, is_new= False):
        if is_new is True:
            row_index = self.widget_table.rowCount()
            self.widget_table.insertRow(row_index)
        else:
            row_index = self.get_row_id(sanding_program.pk)
        add_item_to_table(self.widget_table, row_index, 0, sanding_program.name)
        total_passes_count = models.SandingProgramPass.objects.filter(sanding_program=sanding_program, is_temp=False).count()
        add_item_to_table(self.widget_table, row_index, 1, total_passes_count)
        if is_new is True:
            edit_btn = RecordTrackBtn(sanding_program.pk, ":/icons/icons/icons8-edit-96.png")
            del_btn = RecordTrackBtn(sanding_program.pk, ":/icons/icons/icons8-delete-bin-96.png")
            self.widget_table.setCellWidget(row_index, 2, edit_btn)
            self.widget_table.setCellWidget(row_index, 3, del_btn)
            edit_btn.customClickSignal.connect(self.handle_edit_program)
            del_btn.customClickSignal.connect(self.handle_delete_program)

    def create_new_program(self):
        dia = AddEditSandingProgramDialog(parent=self)
        if dia.exec_():
            added_program = dia.get_current_program()
            self.append_new_sanding_program(added_program, True)
            self.__all_added_programs.add(added_program.name)
            self.programsChanged.emit(self.__all_added_programs)

    def handle_edit_program(self, program_id:int):
        current_program = models.SandingProgram.objects.get(pk=program_id)
        dia = AddEditSandingProgramDialog(current_program, self)
        if dia.exec_():
            updated_program = dia.get_current_program()
            self.append_new_sanding_program(updated_program, False)
            self.__all_added_programs.add(updated_program.name)
            self.programsChanged.emit(self.__all_added_programs)

    def handle_delete_program(self, program_id:int):
        program = self.profile_db_model.objects.get(pk=program_id)
        self.__all_added_programs.remove(program.name)
        program.delete()
        row_id = self.get_row_id(program_id)
        self.widget_table.removeRow(row_id)
        self.programsChanged.emit(self.__all_added_programs)

    def get_row_id(self, item_pk):
        row_id = -1
        for row_index in range(self.widget_table.rowCount()):
            lst_btn = self.widget_table.cellWidget(row_index, self.widget_table.columnCount() - 1)
            if item_pk == lst_btn.get_id():
                row_id = row_index
        if row_id < 0:
            raise ValueError(f"the id field should be > 0 order pk {item_pk}")
        return row_id


    def get_footer_btn_name(self) -> str:
        return self.__footer_btn_text


    def is_dirty(self) -> bool:
        return False

    def new_image_received(self, camera_index, pix_map):
        pass

    def handle_joint_dowel_profile_updated(self, new_profiles):
        pass

    def handle_setting_changed(self):
        pass

    def change_measure_mode(self, unit: MeasureUnitType):
        pass



