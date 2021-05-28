from .generated import Ui_DovetailCameraPageUI
from PySide2 import QtWidgets
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