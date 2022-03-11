from PySide2 import QtWidgets, QtCore

from views.camera_viewer import CameraViewer
from views.serial_monitor_widget import SerialMonitorWidget
from configurations import dovetail_configurations
from configurations import sanding_configuration
from configurations import common_configurations
from custom_widgets.spin_box import CustomSpinBox
from configurations.custom_pram_loader import CustomMachineParamManager
if common_configurations.CURRENT_MACHINE == common_configurations.SupportedMachines.dovetailMachine:
    MACHINE_REST_PAGE_BUTTONS = dovetail_configurations.DOVETAIL_RESET_PAGE_BUTTONS
elif common_configurations.CURRENT_MACHINE == common_configurations.SupportedMachines.sandingMachine:
    MACHINE_REST_PAGE_BUTTONS = sanding_configuration.SANDING_RESET_PAGE_BUTTONS
else:
    raise ValueError("not supported machine....")


class SanderConfigurationWidget(QtWidgets.QFrame):
    stateChangedSignal = QtCore.Signal(int, str, bool)
    def __init__(self, sander_number):
        super(SanderConfigurationWidget, self).__init__()
        self.widget_layout = QtWidgets.QHBoxLayout(self)

        self.__sander_number = sander_number
        self.widget_layout.addWidget(QtWidgets.QLabel(f"Sander {sander_number}:"))
        self.activate_checkbox = QtWidgets.QCheckBox("Activate")
        self.extend_checkbox = QtWidgets.QCheckBox("Extend")
        self.widget_layout.addWidget(self.activate_checkbox)
        self.widget_layout.addWidget(self.extend_checkbox)
        self.activate_checkbox.toggled.connect(self.__handle_activate_toggled)
        self.extend_checkbox.toggled.connect(self.__handle_extend_toggled)
        self.setStyleSheet("QFrame{border:1px solid gray;} QLabel{border:none;}")

    def __handle_activate_toggled(self):
        state = self.activate_checkbox.isChecked()
        self.stateChangedSignal.emit(self.__sander_number, "active", state)
        #self.store_state("active", state)

    def __handle_extend_toggled(self):
        state = self.extend_checkbox.isChecked()
        self.stateChangedSignal.emit(self.__sander_number, "extend", state)
        #self.store_state("extend", state)

    def store_state(self, key, value):
        store_key= f"sander{self.__sander_number}_{key}"
        CustomMachineParamManager.set_value(store_key, value, auto_store=True)



class ResetPageView(QtWidgets.QWidget):
    def __init__(self):
        super(ResetPageView, self).__init__()
        self.sanders_frame = QtWidgets.QFrame()
        self.sanders_frame_layout = QtWidgets.QGridLayout(self.sanders_frame)
        self.sanders_frame_layout.setSpacing(15)
        self.main_grid_layout = QtWidgets.QGridLayout(self)
        self.widgets_grid_layout = QtWidgets.QGridLayout()
        self.camera_grid_layout = QtWidgets.QGridLayout()
        self.serial_monitor_grid_layout = QtWidgets.QGridLayout()
        self.main_grid_layout.addLayout(self.widgets_grid_layout, 0, 0, 1, 2)
        self.main_grid_layout.addWidget(self.sanders_frame, 1, 0, 1, 2)
        self.main_grid_layout.addLayout(self.camera_grid_layout, 2, 0, 1, 1)
        self.main_grid_layout.addLayout(self.serial_monitor_grid_layout, 2, 1, 1, 1)
        # to split the main view
        self.main_grid_layout.setColumnStretch(0, 4)
        self.main_grid_layout.setColumnStretch(1, 4)
        self.main_grid_layout.setRowStretch(0, 1)
        self.main_grid_layout.setRowStretch(1, 1)
        self.main_grid_layout.setRowStretch(2, 4)
        # load the widgets
        # we will but for widgets in each row

       # create sander widgets
        self.sander_widgets = list()
        for i in range(4):
            sander_widget = SanderConfigurationWidget(i+1)
            self.sander_widgets.append(sander_widget)
            self.sanders_frame_layout.addWidget(sander_widget, i//3, i%3, 1, 1)
        # create pressure widget
        self.__pressure_layout = QtWidgets.QHBoxLayout()
        self.__pressure_layout.addWidget(QtWidgets.QLabel("Pressure"))
        self.pressure_widget = CustomSpinBox(
            *(0, 30, 1),
            initial_mm=0,
            disp_precession=0,
            target_config_key="reset_pressure_value",
            numpad_title="Pressure",
            allow_mode_change= False
        )
        self.pressure_widget.setMinimumWidth(300)
        self.__pressure_layout.addWidget(self.pressure_widget)
        self.__pressure_layout.addStretch(1)
        i += 1
        self.sanders_frame_layout.addLayout(self.__pressure_layout, i // 3, i % 3, 1, 1)

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
