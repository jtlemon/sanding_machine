from PySide2 import QtWidgets, QtCore

from models import MeasureUnitType
from view_managers.abs_operation_widget_manager import AbstractOperationWidgetManger



class IndividualSandpaperOperations(QtWidgets.QWidget, AbstractOperationWidgetManger):
    selectedProfileChanged = QtCore.Signal(str, str)
    def __init__(self, footer_btn="Sandpaper"):
        super(IndividualSandpaperOperations, self).__init__()
        self.__footer_btn_text = footer_btn
        # create dynamic widgets


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

