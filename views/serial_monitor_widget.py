from PySide2 import QtWidgets, QtCore


class SerialMonitorWidget(QtWidgets.QGroupBox):
    monitorSendCmdSignal = QtCore.Signal(str)

    def __init__(self):
        super(SerialMonitorWidget, self).__init__()
        self.setTitle("Grbl Serial Monitor")
        self.widget_layout = QtWidgets.QVBoxLayout(self)
        self.cmd_to_send_line = QtWidgets.QLineEdit()
        self.cmd_to_send_line.setObjectName("monitor_cmd_to_send_line")
        self.cmd_to_send_line.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.widget_layout.addWidget(self.cmd_to_send_line)
        self.send_btn = QtWidgets.QPushButton("send")
        self.send_btn.setObjectName("monitor_send_btn")
        self.send_btn.setFixedSize(120, 40)
        self.widget_layout.addWidget(self.send_btn, stretch=0, alignment=QtCore.Qt.AlignRight)
        self.received_response_browser = QtWidgets.QTextBrowser()
        self.received_response_browser.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        self.received_response_browser.setObjectName("monitor_received_response_browser")
        self.widget_layout.addWidget(self.received_response_browser)
        self.clear_btn = QtWidgets.QPushButton("Clear")
        self.clear_btn.setObjectName("monitor_clear_btn")
        self.clear_btn.setFixedSize(120, 40)
        self.widget_layout.addWidget(self.clear_btn, stretch=0, alignment=QtCore.Qt.AlignCenter)
        self.clear_btn.clicked.connect(lambda: self.received_response_browser.clear())
        self.send_btn.clicked.connect(self.send_command)
        self.cmd_to_send_line.returnPressed.connect(self.send_command)

    def send_command(self):
        cmd_to_send = self.cmd_to_send_line.text().strip()
        if len(cmd_to_send) > 0:
            self.monitorSendCmdSignal.emit(cmd_to_send)
            self.cmd_to_send_line.setText("")

    def response_received(self, response_list: list):
        for response_dict in response_list:
            cmd_to_send = response_dict.get("cmd", "").strip("\r\n")
            response = response_dict.get("response", "").strip("\r\n")
            if len(cmd_to_send) > 0:
                self.received_response_browser.append(f">> {cmd_to_send}")
            if len(response) > 0:
                self.received_response_browser.append(f"<< {response}")


if __name__ == "__main__":
    from views import utils

    app = QtWidgets.QApplication([])
    utils.load_app_fonts()
    w = SerialMonitorWidget()
    w.show()
    app.setStyleSheet(utils.load_app_style())
    app.exec_()
