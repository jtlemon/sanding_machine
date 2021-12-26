from PySide2 import QtWidgets

from views.camera_viewer import CameraViewer
from views.serial_monitor_widget import SerialMonitorWidget
from configurations import dovetail_configurations
from configurations import sanding_configuration
from configurations import common_configurations

if common_configurations.CURRENT_MACHINE == common_configurations.SupportedMachines.dovetailMachine:
    MACHINE_REST_PAGE_BUTTONS = dovetail_configurations.DOVETAIL_RESET_PAGE_BUTTONS
elif common_configurations.CURRENT_MACHINE == common_configurations.SupportedMachines.sandingMachine:
    MACHINE_REST_PAGE_BUTTONS = sanding_configuration.SANDING_RESET_PAGE_BUTTONS
else:
    raise ValueError("not supported machine....")


class ResetPageView(QtWidgets.QWidget):
    def __init__(self):
        super(ResetPageView, self).__init__()
        self.main_grid_layout = QtWidgets.QGridLayout(self)
        self.widgets_grid_layout = QtWidgets.QGridLayout()
        self.camera_grid_layout = QtWidgets.QGridLayout()
        self.serial_monitor_grid_layout = QtWidgets.QGridLayout()
        self.main_grid_layout.addLayout(self.widgets_grid_layout, 0, 0, 1, 2)
        self.main_grid_layout.addLayout(self.camera_grid_layout, 1, 0, 1, 1)
        self.main_grid_layout.addLayout(self.serial_monitor_grid_layout, 1, 1, 1, 1)
        # to split the main view
        self.main_grid_layout.setColumnStretch(0, 4)
        self.main_grid_layout.setColumnStretch(1, 2)
        self.main_grid_layout.setRowStretch(0, 1)
        self.main_grid_layout.setRowStretch(1, 4)
        # load the widgets
        # we will but for widgets in each row
        no_of_buttons_per_row = 4
        buttons_counts = len(MACHINE_REST_PAGE_BUTTONS)
        for i in range(buttons_counts):
            btn_config_dict = MACHINE_REST_PAGE_BUTTONS[i]
            btn = QtWidgets.QPushButton(btn_config_dict.get("lbl"))
            btn.setFixedHeight(60)
            btn.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
            setattr(self, btn_config_dict.get("target_key"), btn)
            row_index = i // no_of_buttons_per_row
            col_index = i % no_of_buttons_per_row
            self.widgets_grid_layout.addWidget(btn, row_index, col_index, 1, 1)

        self.camera_viewer = CameraViewer([cam_index for cam_index in range(common_configurations.AVAILABLE_CAMERAS)])
        self.serial_monitor_widget = SerialMonitorWidget()
        self.camera_grid_layout.addWidget(self.camera_viewer, 0, 0, 1, 1)
        self.serial_monitor_grid_layout.addWidget(self.serial_monitor_widget, 0, 0, 1, 1)

    def new_image_received(self, camera_index, pix_map):
        self.camera_viewer.new_image_received(camera_index, pix_map)


if __name__ == "__main__":
    from views import utils

    app = QtWidgets.QApplication([])
    utils.load_app_fonts()
    w = ResetPageView()
    w.showMaximized()
    app.setStyleSheet(utils.load_app_style())
    app.exec_()
