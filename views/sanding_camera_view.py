from .generated import Ui_DovetailCameraPageUI
from PySide2 import QtWidgets, QtCore
from views.camera_viewer import CameraViewer
import configurations.static_app_configurations as static_configurations
from models import MeasureUnitType

class SandingCameraPageView(QtWidgets.QWidget):
    def __init__(self):
        super(SandingCameraPageView, self).__init__()
        self.widget_layout = QtWidgets.QGridLayout(self)
        self.camera_viewer = CameraViewer([cam_index for cam_index in range(static_configurations.AVAILABLE_CAMERAS)])
        self.widget_layout.addWidget(self.camera_viewer)

    def new_image_received(self, camera_index, pix_map):
        self.camera_viewer.new_image_received(camera_index, pix_map)

    def change_measure_mode(self, unit: MeasureUnitType):
        pass

