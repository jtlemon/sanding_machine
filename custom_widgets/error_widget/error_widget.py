from PySide2 import QtWidgets, QtCore


class ErrorWidgetLabel(QtWidgets.QLabel):
    def __init__(self):
        super(ErrorWidgetLabel, self).__init__()
        self.__colors  = ["black", "red"]
        self.current_color_index = 0
        self.__flashing_timer = QtCore.QTimer()
        self.__flashing_timer.timeout.connect(self._manage_color_change)

    def _manage_color_change(self):
        self.current_color_index = (self.current_color_index + 1) % 2
        self.setStyleSheet(f"color:{self.__colors[self.current_color_index]}")

    def set_error(self, error_dict:dict):
        flashing_required =  error_dict.get("flashing", False)
        self.__colors[1]  = error_dict.get("color", "black")
        self.setText(error_dict.get("txt", "red"))
        if flashing_required:
            self.__flashing_timer.start(500)
        else:
            self.setStyleSheet(f"color:{self.__colors[1]}")

    def clr_errors(self):
        self.setText("")
        self.__flashing_timer.stop()
        self.setStyleSheet(f"color:{self.__colors[0]}")
        self.current_color_index = 0





