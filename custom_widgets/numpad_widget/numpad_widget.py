from PySide2 import QtWidgets,QtCore
from .numpad_widget_gen import Ui_numpad

class NumpadWidget(QtWidgets.QDialog , Ui_numpad):
    def __init__(self,min_val,max_val,current_value_mm,title=""):
        super(NumpadWidget, self).__init__()
        self.setupUi(self)
        self.__current_value_mm = current_value_mm
        self.__min_val_mm = min_val
        self.__max_val_mm = max_val
        self.__current_digits = ""
        self.__saved_value = self.__current_value_mm
        self.__current_mode = "mm"
        # install signals
        self.btn_0.clicked.connect(lambda: self.button_pressed("0"))
        self.btn_1.clicked.connect(lambda :self.button_pressed("1"))
        self.btn_2.clicked.connect(lambda: self.button_pressed("2"))
        self.btn_3.clicked.connect(lambda: self.button_pressed("3"))
        self.btn_4.clicked.connect(lambda: self.button_pressed("4"))
        self.btn_5.clicked.connect(lambda: self.button_pressed("5"))
        self.btn_6.clicked.connect(lambda: self.button_pressed("6"))
        self.btn_7.clicked.connect(lambda: self.button_pressed("7"))
        self.btn_8.clicked.connect(lambda: self.button_pressed("8"))
        self.btn_9.clicked.connect(lambda: self.button_pressed("9"))
        self.btn_dot.clicked.connect(lambda: self.button_pressed("."))
        self.btn_clear.clicked.connect(lambda: self.button_pressed("c"))
        self.btn_in.clicked.connect(self.change_mode)
        self.btn_reset.clicked.connect(self.reset_defaults)
        self.btn_save.clicked.connect(self.save_value)

        self.__last_char = ""
        self.blink_timer = QtCore.QTimer()
        self.blink_timer.timeout.connect(self._flash_last_digit)
        self.blink_timer.start(500)
        self.disp_pannel.setText(self.__current_digits)
        self.min_val.setText("%.2f"%(self.__min_val_mm))
        self.max_val.setText("%.2f"%(self.__max_val_mm))
        self.setModal(True)
        self.setWindowTitle(title)
        self.show()

    def reset_defaults(self):
        if self.__current_mode == "mm":
            self.__current_digits = str(self.__current_value_mm)
        else:
            values_in_inch = round(self.__current_value_mm/25.4, 4)
            self.__current_digits = str(values_in_inch)
        self.disp_pannel.setText(self.__current_digits)

    def change_mode(self):
        try:
            current_val = float(self.__current_digits)
        except ValueError:
            current_val = 0
        if self.__current_mode == "mm":
            self.__current_mode = "\""
            self.min_val.setText("%.3f"%(self.__min_val_mm/25.4))
            self.max_val.setText("%.3f"%(self.__max_val_mm/25.4))
            self.btn_in.setStyleSheet("background-color:green;")
        else:
            self.__current_mode = "mm"
            self.min_val.setText("%.2f" % (self.__min_val_mm))
            self.max_val.setText("%.2f" % (self.__max_val_mm))
            self.btn_in.setStyleSheet("background-color:white;")
        self.min_unit.setText('{}'.format(self.__current_mode))
        self.max_unit.setText('{}'.format(self.__current_mode))
        self.disp_unit.setText('{}'.format(self.__current_mode))
        self.__current_digits = ""
        self.disp_pannel.setText(self.__current_digits)

    def button_pressed(self, val):
        if val == "c":
            self.__current_digits = ""
        elif val == ".":
            if "." not in self.__current_digits:
                self.__current_digits += val
        else:
            self.__current_digits += val
        self.disp_pannel.setText(self.__current_digits)

    def _flash_last_digit(self):
        if self.__last_char =="":
            self.__last_char = "_"
        else:
            self.__last_char = ""
        self.disp_pannel.setText(self.__current_digits+self.__last_char)

    def save_value(self):
        try:
            current_value = float(self.__current_digits)
            if self.__current_mode == '"':
                current_value_mm = current_value*25.4
            else:
                current_value_mm = current_value
            if current_value_mm < self.__min_val_mm or current_value_mm > self.__max_val_mm:
                min_range = self.__min_val_mm
                max_range = self.__max_val_mm
                if self.__current_mode == '"':
                    min_range = round(min_range/25.4 , 4)
                    max_range = round(max_range/25.4 , 4)
                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Warning)
                msg.setWindowTitle("Range Error")
                msg.setText("valid value must be between {} and {}".format(min_range, max_range))
                msg.exec_()
                return
            self.__saved_value = current_value_mm
            self.accept()

        except ValueError:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setWindowTitle("Value")
            if len(self.__current_digits) == 0:
                 msg.setText("value couldn't be empty")
            else:
                msg.setText("pls enter valid number")
            msg.exec_()

    def get_value(self):
        return self.__saved_value




def __TEST__():
    app = QtWidgets.QApplication()
    dia = NumpadWidget(20,50,23)
    dia.exec_()
    app.exec_()
if __name__ == "__main__":
    __TEST__()


