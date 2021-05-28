from PySide2 import QtWidgets

from models import MeasureUnitType
from .abs_operation_widget_manager import AbstractOperationWidgetManger


class JointSettingPageManger(QtWidgets.QWidget, AbstractOperationWidgetManger):
    def __init__(self, footer_btn):
        super(JointSettingPageManger, self).__init__()
        self.__footer_btn_text = footer_btn

    def change_mode(self, unit: MeasureUnitType):
        raise NotImplementedError('subclasses must override change_mode()!')

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
