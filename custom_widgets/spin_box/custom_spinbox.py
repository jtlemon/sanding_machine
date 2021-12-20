from enum import Enum

from PySide2 import QtWidgets, QtCore

from configurations.custom_pram_loader import CustomMachineParamManager
from custom_widgets.numpad_widget import NumpadWidget
from . import custom_spinbox_gen as main_view
from . import two_button_combo_view as buttons_view


class SpinType(Enum):
    addSubType = 0
    leftRightType = 1
    upDownType = 2


class SpinUnitMode(Enum):
    MM_MODE = 0
    IN_MODE = 1


class CustomSpinBox(QtWidgets.QFrame, main_view.Ui_Frame, buttons_view.Ui_Frame):
    class_objects = []
    valueChanged = QtCore.Signal(float)

    def __init__(self,
                 min_val_mm,
                 max_val_mm,
                 step_mm,
                 initial_mm,
                 allow_mode_change=True,
                 disp_precession=1,
                 special_lbl={},
                 extra="",
                 div_factor=25.4,
                 numpad_title="",
                 display_numpad_enabled=True,
                 display_type=SpinType.addSubType,
                 display_relative=False,
                 target_config_key=""
                 ):
        super(CustomSpinBox, self).__init__()
        if display_type == SpinType.addSubType:
            main_view.Ui_Frame.setupUi(self, self)
        else:
            buttons_view.Ui_Frame.setupUi(self, self)

        self.__target_config_key = target_config_key
        self.__initial_value_changed_flag = False
        self.__numpad_display_title = numpad_title
        self.__DIV_FACTOR = div_factor
        self.__DISP_PRECESSION = disp_precession
        self.__allow_mode_change = allow_mode_change
        self.__current_val_mm = 0  # hold current value in mm
        self.__min_val = min_val_mm
        self.__max_val = max_val_mm
        self.__original_val__mm = initial_mm
        self.__current_mode = SpinUnitMode.MM_MODE
        self.display_type = display_type
        self.__use_relative_value = display_relative
        if len(special_lbl) == 0:
            self.__unit_mapper = {SpinUnitMode.MM_MODE: "mm", SpinUnitMode.IN_MODE: '"'}
        else:
            self.__unit_mapper = special_lbl
        self.__step = step_mm
        self.inc_btn.setAutoRepeat(True)
        self.inc_btn.setAutoRepeatDelay(300)
        self.dec_btn.setAutoRepeat(True)
        self.dec_btn.setAutoRepeatDelay(300)
        CustomSpinBox.class_objects.append(self)
        self.setFixedHeight(70)
        if not self.__allow_mode_change:
            self.unit_lbl.setHidden(True)
            if len(extra) > 0:
                self.extra_lbl.setText(extra)
        if len(extra) == 0:
            self.extra_lbl.setHidden(True)

        if self.display_type == SpinType.addSubType:
            self.inc_btn.clicked.connect(lambda: self._update_val("inc"))
            self.dec_btn.clicked.connect(lambda: self._update_val("dec"))


        elif self.display_type == SpinType.leftRightType:
            self.inc_btn.setText("right")
            self.dec_btn.setText("left")
            self.inc_btn.clicked.connect(lambda: self._update_val("inc"))
            self.dec_btn.clicked.connect(lambda: self._update_val("dec"))
        elif self.display_type == SpinType.upDownType:
            # if we increase the number it moves down
            self.inc_btn.setText("up")
            self.dec_btn.setText("down")
            self.inc_btn.clicked.connect(lambda: self._update_val("dec"))  # up button
            self.dec_btn.clicked.connect(lambda: self._update_val("inc"))

        frame_radius = self.height() // 2
        btn_radius = self.inc_btn.height() // 2
        if display_numpad_enabled:
            self.val_lbl.mousePressEvent = self.open_numpad
        self.set_display_mode()
        self.set_value(initial_mm)

        self.setStyleSheet(
            '''
            QFrame
            {
                 border-radius:%dpx;
                border-color: rgb(238, 238, 236);    
            }
            QWidget
            {
                
                background-color: rgb(211, 215, 207);
            }
            
            QToolButton ,QPushButton
            {
                /*border:none;*/
               border:none;
              border-radius:%dpx;
               
            }
            QToolButton:pressed , QPushButton:pressed
            {
                /*border:none;*/
               border:2px solid rgb(255,255,255);
                background-color: rgb(255, 255, 255);
              border-radius:%dpx;
               
            }
            QLabel
            {
               font-size:18px;
            }
            ''' % (frame_radius, btn_radius, btn_radius)
        )


    def set_display_mode(self, mode=SpinUnitMode.MM_MODE):
        if self.__allow_mode_change:
            if mode == SpinUnitMode.MM_MODE or mode == SpinUnitMode.IN_MODE:
                self.__current_mode = mode
                self.unit_lbl.setText(self.__unit_mapper[mode])
                self._update_display()
            else:
                raise ValueError("mode must be mm or in")
        else:
            self.__current_mode = SpinUnitMode.MM_MODE

    def set_value(self, value_in_mm, update_display=True, emit_change_signal=False, extra_lbl=None):
        self.__current_val_mm = value_in_mm
        if update_display:
            self._update_display(extra_lbl)
        if emit_change_signal:
            self.valueChanged.emit(self.__current_val_mm)

    def value(self):
        return self.__current_val_mm

    def store(self, auto_save=True):
        if self.is_changed():
            CustomMachineParamManager.set_value(self.__target_config_key, self.__current_val_mm, auto_save)
        self.__original_val__mm = self.__current_val_mm
        self._update_display()

    def reset_state(self):
        self.__original_val__mm = self.__current_val_mm
        self._update_display()

    def set_value_and_reset_state(self, value_in_mm):
        self.set_value(value_in_mm)
        self.__original_val__mm = self.__current_val_mm
        self._update_display()

    def text(self):
        return str(self.__current_val_mm)

    def _update_val(self, opt, lbl=None):
        if opt == "inc":
            if self.__current_val_mm < self.__max_val:
                tmp = round(self.__current_val_mm + self.__step, 3)
                if tmp <= self.__max_val:
                    self.set_value(tmp, emit_change_signal=True, extra_lbl=lbl)
        else:
            if self.__current_val_mm > self.__min_val:
                tmp = round(self.__current_val_mm - self.__step, 3)
                if tmp >= self.__min_val:
                    self.set_value(tmp, emit_change_signal=True, extra_lbl=lbl)

    def _update_display(self, extra_lbl=None):
        if not self.is_changed():
            self.val_lbl.setStyleSheet("color:black")
        else:
            self.val_lbl.setStyleSheet("color:red")

        current_val = self.__current_val_mm
        if self.__use_relative_value:
            current_val = current_val - self.__original_val__mm
        if self.__current_mode == SpinUnitMode.MM_MODE:
            txt_to_dis = f"{current_val :.{self.__DISP_PRECESSION}f}"
        else:
            current_val_in = current_val / self.__DIV_FACTOR
            txt_to_dis = f"{current_val_in:.3f}"
        if extra_lbl is None:
            self.val_lbl.setText(txt_to_dis)
        else:
            self.val_lbl.setText(extra_lbl)

    def is_changed(self):
        return True if self.__original_val__mm != self.__current_val_mm else False

    def restore_original(self):
        self.set_value(self.__original_val__mm, emit_change_signal=True)

    def open_numpad(self, ev):
        setting_dialog = NumpadWidget(self.__min_val, self.__max_val, self.__current_val_mm,
                                      self.__numpad_display_title)
        if self.__current_mode != SpinUnitMode.MM_MODE:
            setting_dialog.change_mode()
        has_to_save = setting_dialog.exec_()
        if has_to_save:
            val_in_mm = setting_dialog.get_value()
            if self.__use_relative_value:
                val_in_mm = self.__current_val_mm + val_in_mm
            self.set_value(val_in_mm, emit_change_signal=True)

    def get_key(self):
        return  self.__target_config_key




def __TEST__():
    app = QtWidgets.QApplication([])
    dia = CustomSpinBox(0, 10, 1, 3, display_type=SpinType.leftRightType)
    dia.show()
    app.exec_()


if __name__ == "__main__":
    __TEST__()
