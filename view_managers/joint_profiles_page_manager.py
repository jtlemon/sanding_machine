from PySide2 import QtWidgets, QtCore
from models import MeasureUnitType
from view_managers.abs_operation_widget_manager import AbstractOperationWidgetManger
from views import DovetailCameraPageView
from configurations.custom_pram_loader import CustomMachineParamManager

import configurations.static_app_configurations as static_configurations






class JointProfilesPageManager(QtWidgets.QWidget):
    def __init__(self, footer_btn):
        super(JointProfilesPageManager, self).__init__()
        self.__footer_btn_text = footer_btn
        if static_configurations.CURRENT_MACHINE == static_configurations.SupportedMachines.dovetailMachine:
             supported_joint_profiles = static_configurations.DOVETAIL_JOINT_PROFILE_CONFIGURATION
        else:
            raise ValueError("not supported machine.......")
        # i will assume that i will divid the widgets into 2 cols
        self.v_widget_layout = QtWidgets.QVBoxLayout()
        self.spin_box_layout = QtWidgets.QGridLayout()
        self.joint_profiles_spinbox_widgets = list()

        self.spin_box_layout.setSpacing(20)
        v_spacer_item_1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Preferred,
                                                QtWidgets.QSizePolicy.Expanding)
        self.v_widget_layout.addItem(v_spacer_item_1)
        self.v_widget_layout.addLayout(self.spin_box_layout)
        v_spacer_item_2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Preferred,
                                                QtWidgets.QSizePolicy.Expanding)
        self.v_widget_layout.addItem(v_spacer_item_2)
        self.setLayout(self.v_widget_layout)



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
        pass



