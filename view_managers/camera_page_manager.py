from PySide2 import QtWidgets
from models import MeasureUnitType
from .abs_operation_widget_manager import AbstractOperationWidgetManger
from views import DovetailCameraPageView


class DovetailCameraPageManager(DovetailCameraPageView, AbstractOperationWidgetManger):
    def __init__(self, footer_btn):
        super(DovetailCameraPageManager, self).__init__()
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

    def new_image_received(self, camera_index, pix_map):
        if camera_index == 0:
            self.camera_display.setPixmap(pix_map)

    def handle_joint_profile_updated(self, new_profile):
        self.available_profiles_combo.load_new_options(new_profile)

