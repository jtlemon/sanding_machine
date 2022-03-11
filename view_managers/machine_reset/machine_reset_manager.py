from models import MeasureUnitType
from views.reset_page import ResetPageView
from PySide2 import QtCore
from models.sensors_connector_hal import SensorConnector
from models.sander_generate import sander_dictionary


class ResetPageManager(ResetPageView):
    def __init__(self, grbl_interface_ref, sensors_board_ref:SensorConnector):
        super(ResetPageManager, self).__init__()
        self.__footer_btn_text = "Reset"
        self.__grbl_interface_ref = grbl_interface_ref
        self.__sensors_board_ref = sensors_board_ref
        self.reset_controller_btn.clicked.connect(grbl_interface_ref.reset_machine)
        #self.home_btn.clicked.connect(grbl_interface_ref.reset_and_home)
        self.go_to_park_btn.clicked.connect(grbl_interface_ref.park)
        self.serial_monitor_widget.monitorSendCmdSignal.connect(lambda cmd:
                                                                grbl_interface_ref.grbl_stream.send_direct_command(
                                                                    cmd,
                                                                    clr_buffer=True
                                                                ))
        self.pressure_widget.valueChanged.connect(self.__handle_pressure_changed)
        for sander_widget in self.sander_widgets:
            sander_widget.stateChangedSignal.connect(self.handle_sander_checkbox_changed)

        self.__response_checker = QtCore.QTimer()
        self.__response_checker.setSingleShot(False)
        self.__response_checker.timeout.connect(self.get_latest_responses)
        self.__response_checker.start(200)

    def handle_sander_checkbox_changed(self, sander_no:int, key:str, state:bool):
        if key == "active":
            state_str = "on" if state else "off"
        else:
            state_str = "extend" if state else "retract"
        cmd = sander_dictionary[sander_no][state_str]
        self.__grbl_interface_ref.grbl_stream.send_direct_command(
            cmd,
            clr_buffer=True
        )

    def __handle_pressure_changed(self, new_pressure):
        new_pressure = int(new_pressure)
        self.__sensors_board_ref.send_pressure_value(new_pressure)


    def get_footer_btn_name(self) -> str:
        return self.__footer_btn_text

    def is_dirty(self) -> bool:
        return False

    def change_measure_mode(self, unit: MeasureUnitType):
        pass

    def get_latest_responses(self):
        responses = self.__grbl_interface_ref.get_latest_responses()
        self.serial_monitor_widget.response_received(responses)

