from .generated import Ui_DovetailCameraPageUI
from PySide2 import QtWidgets, QtCore
from custom_widgets.dovetail_buttons_widget import DovetailSideButtons
import configurations.static_app_configurations as app_configurations


class DovetailCameraPageView(QtWidgets.QWidget, Ui_DovetailCameraPageUI):
    def __init__(self):
        super(DovetailCameraPageView, self).__init__()
        self.setupUi(self)
        self.sidebar_frame_layout = QtWidgets.QVBoxLayout(self.sidebar_frame)
        self.side_buttons_widget = DovetailSideButtons(app_configurations.DOVETAIL_SUPPORTED_LEVELS)
        self.sidebar_frame_layout.addWidget(self.side_buttons_widget)
        v_spacer_item_1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Preferred,
                                                QtWidgets.QSizePolicy.Expanding)
        self.sidebar_frame_layout.addItem(v_spacer_item_1)
        self.measure_tool_btn = QtWidgets.QPushButton("measure tool")
        self.measure_tool_btn.setFixedHeight(60)
        self.measure_tool_btn.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.sidebar_frame_layout.addWidget(self.measure_tool_btn)

        self.loaded_bit_lbl = QtWidgets.QLabel("loaded bit name")
        self.loaded_bit_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.sidebar_frame_layout.addWidget(self.loaded_bit_lbl)
        self.change_bit_btn = QtWidgets.QPushButton("Change Machine Bit")
        self.change_bit_btn.setFixedHeight(60)
        self.change_bit_btn.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.sidebar_frame_layout.addWidget(self.change_bit_btn)

        self.start_button.setCheckable(True)
        self.cancel_Button.setCheckable(True)
        self.camera_display.setMaximumSize(640, 360)
