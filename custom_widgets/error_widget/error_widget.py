from PySide2 import QtWidgets, QtCore


class ErrorWidgetLabel(QtWidgets.QLabel):
    def __init__(self):
        super(ErrorWidgetLabel, self).__init__()
        self.__colors = ["black", "red"]
        self.current_color_index = 0
        self.__flashing_timer = QtCore.QTimer()
        self.__flashing_timer.timeout.connect(self._manage_color_change)

    def _manage_color_change(self):
        self.current_color_index = (self.current_color_index + 1) % 2
        self.setStyleSheet(f"color:{self.__colors[self.current_color_index]}")

    def set_error(self, alarm_text, preferred_color="red"):
        self.__colors[1] = preferred_color
        self.__flashing_timer.start(500)
        self.setText(alarm_text)

    def clr_errors(self):
        self.setText("No Alarms")
        self.__flashing_timer.stop()
        self.setStyleSheet(f"color:{self.__colors[0]}")
        self.current_color_index = 0
