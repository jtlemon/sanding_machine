from PySide2 import QtWidgets, QtCore

from models import MeasureUnitType
from .abs_operation_widget_manager import AbstractOperationWidgetManger
from views.sanding_camera_view import SandingCameraPageView


class SandingCameraPageManager(SandingCameraPageView, AbstractOperationWidgetManger):
    selectedProfileChanged = QtCore.Signal(str, str)
    def __init__(self, footer_btn="Main"):
        super(SandingCameraPageManager, self).__init__()
        self.__footer_btn_text = footer_btn
        # create dynamic widgets




    def change_measure_mode(self, unit: MeasureUnitType):
        pass


    def get_footer_btn_name(self) -> str:
        return self.__footer_btn_text


    def is_dirty(self) -> bool:
        return False


    def handle_joint_dowel_profile_updated(self, new_profiles):
        pass

    def handle_setting_changed(self):
        pass

    def change_measure_mode(self, unit: MeasureUnitType):
        pass



