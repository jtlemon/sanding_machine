from models import MeasureUnitType
from views.reset_page import ResetPageView
from PySide2 import QtCore

class ResetPageManager(ResetPageView):
    def __init__(self, grbl_interface_ref):
        super(ResetPageManager, self).__init__()
        self.__footer_btn_text = "Reset"
        self.__grbl_interface_ref = grbl_interface_ref
        self.reset_controller_btn.clicked.connect(grbl_interface_ref.reset_machine)
        self.go_to_park_btn.clicked.connect(grbl_interface_ref.park)
        self.serial_monitor_widget.monitorSendCmdSignal.connect(lambda cmd:
                                                                grbl_interface_ref.grbl_stream.send_direct_command(
                                                                    cmd,
                                                                    clr_buffer=True
                                                                ))

        self.__response_checker = QtCore.QTimer()
        self.__response_checker.setSingleShot(False)
        self.__response_checker.timeout.connect(self.get_latest_responses)
        self.__response_checker.start(200)

    def get_footer_btn_name(self) -> str:
        return self.__footer_btn_text

    def is_dirty(self) -> bool:
        return False

    def change_measure_mode(self, unit: MeasureUnitType):
        pass

    def get_latest_responses(self):
        responses = self.__grbl_interface_ref.get_latest_responses()
        self.serial_monitor_widget.response_received(responses)

