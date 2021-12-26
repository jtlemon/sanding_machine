import os
try:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
except Exception as e:
    print(e)
from apps.sanding_machine import models
from PySide2 import QtWidgets, QtCore
from view_managers.sanding_modules.door_styles.add_edit_door_style_dialog import  AddEditDoorStyleDialog
from models.custom_app_types import MeasureUnitType
from views.custom_app_widgets import ProfileAddEditWidget
from view_managers.abs_operation_widget_manager import AbstractOperationWidgetManger
from configurations import sanding_configuration





class SandingDoorStylesManager(ProfileAddEditWidget, AbstractOperationWidgetManger):
    profileChanged = QtCore.Signal(set)
    def __init__(self, footer_btn="Door Styles"):
        super(SandingDoorStylesManager, self).__init__(sanding_configuration.SANDING_DOOR_STYLES_PROFILE,
                                                       add_edit_dialog_class=AddEditDoorStyleDialog,
                                                       db_model=models.DoorStyle,
                                                       append_bit_profile= False)
        self.__sanding_door_styles = set()
        self.__footer_btn_text = footer_btn



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
    utils.load_app_fonts()
    #
    joint_profile = SandingDoorStylesManager()
    app.setStyleSheet(utils.load_app_style())
    joint_profile.showMaximized()
    app.exec_()



