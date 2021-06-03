from enum import Enum
from PySide2 import QtWidgets, QtCore

class ClickedButtonDir(Enum):
    none = 0
    left = 1
    right = 2
    both = 3


class LeftRightCenterButtonWidget(QtWidgets.QWidget):
    btnClicked = QtCore.Signal(int, object)

    def __init__(self, lvl):
        super(LeftRightCenterButtonWidget, self).__init__()
        self.__target_lvl = lvl
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.widget_layout = QtWidgets.QHBoxLayout(self)
        self.widget_layout.setSpacing(0)
        self.setFixedHeight(80)
        # create ui
        self.left_btn = QtWidgets.QPushButton("left")
        self.left_btn.setObjectName("left_btn_widget")
        self.left_btn.setCheckable(True)
        self.left_btn.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        self.widget_layout.addWidget(self.left_btn)
        self.center_btn = QtWidgets.QPushButton(f"L{lvl}")
        self.center_btn.setCheckable(True)
        self.center_btn.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        self.widget_layout.addWidget(self.center_btn)
        self.right_btn = QtWidgets.QPushButton("right")
        self.right_btn.setObjectName("right_btn_widget")
        self.right_btn.setCheckable(True)
        self.right_btn.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        self.widget_layout.addWidget(self.right_btn)
        if lvl == 0:
            self.left_btn.setProperty("offLvl", "1")
            self.right_btn.setProperty("offLvl", "1")
            self.center_btn.setText("off")

        self.__current_btn_active = ClickedButtonDir.none
        self.left_btn.clicked.connect(lambda: self.btnClicked.emit(lvl, ClickedButtonDir.left))
        self.center_btn.clicked.connect(lambda: self.btnClicked.emit(lvl, ClickedButtonDir.both))
        self.right_btn.clicked.connect(lambda: self.btnClicked.emit(lvl, ClickedButtonDir.right))

    def get_current_active_dir(self):
        return self.__current_btn_active

    def is_right_active(self):
        return True if self.__current_btn_active == ClickedButtonDir.both or self.__current_btn_active == ClickedButtonDir.right else False

    def is_left_active(self):
        return True if self.__current_btn_active == ClickedButtonDir.both or self.__current_btn_active == ClickedButtonDir.left else False

    def set_left_active(self):
        self.left_btn.setChecked(True)
        if self.__current_btn_active == ClickedButtonDir.right:
            self.__current_btn_active = ClickedButtonDir.both
        elif self.__current_btn_active != ClickedButtonDir.both:
            self.__current_btn_active = ClickedButtonDir.left

    def set_left_disable(self):
        self.left_btn.setChecked(False)
        if self.__current_btn_active == ClickedButtonDir.both:
            self.__current_btn_active = ClickedButtonDir.right
        elif self.__current_btn_active == ClickedButtonDir.left:
            self.__current_btn_active = ClickedButtonDir.none

    def set_right_active(self):
        self.right_btn.setChecked(True)
        if self.__current_btn_active == ClickedButtonDir.left:
            self.__current_btn_active = ClickedButtonDir.both
        elif self.__current_btn_active != ClickedButtonDir.both:
            self.__current_btn_active = ClickedButtonDir.right

    def set_right_disable(self):
        self.right_btn.setChecked(False)
        if self.__current_btn_active == ClickedButtonDir.both:
            self.__current_btn_active = ClickedButtonDir.left
        elif self.__current_btn_active == ClickedButtonDir.right:
            self.__current_btn_active = ClickedButtonDir.none

    def disable_two_sides(self):
        self.right_btn.setChecked(False)
        self.left_btn.setChecked(False)
        self.__current_btn_active = ClickedButtonDir.none

    def enable_two_sides(self):
        self.right_btn.setChecked(True)
        self.left_btn.setChecked(True)
        self.__current_btn_active = ClickedButtonDir.both

    def set_mid_btn_text(self, text):
        self.center_btn.setText(text)


class DovetailSideButtons(QtWidgets.QWidget):
    sideBtnClicked = QtCore.Signal(int, int)  # current active levels

    def __init__(self, no_of_lvl):
        super(DovetailSideButtons, self).__init__()
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.widget_layout = QtWidgets.QVBoxLayout(self)
        self.widget_layout.setSpacing(12)
        self.button_widgets_list = list()
        for i in range(no_of_lvl):
            btn_widget = LeftRightCenterButtonWidget(i)
            btn_widget.setFixedHeight(70)
            self.widget_layout.addWidget(btn_widget)
            btn_widget.btnClicked.connect(self._handle_btn_widget_pressed)
            self.button_widgets_list.append(btn_widget)

        self.button_widgets_list[0].center_btn.click()



    def _handle_btn_widget_pressed(self, lvl, btn_dir: ClickedButtonDir):
        for i in range(len(self.button_widgets_list)):
            btn_widget = self.button_widgets_list[i]
            btn_widget.center_btn.setChecked(False)
            if btn_dir == ClickedButtonDir.left:
                if i == lvl:
                    btn_widget.set_left_active()
                else:
                    btn_widget.set_left_disable()
            elif btn_dir == ClickedButtonDir.right:
                if i == lvl:
                    btn_widget.set_right_active()
                else:
                    btn_widget.set_right_disable()
            elif btn_dir == ClickedButtonDir.both:
                if i == lvl:
                    btn_widget.enable_two_sides()
                else:
                    btn_widget.disable_two_sides()
        right_active_lvl = -1
        left_active_lvl = -1
        for i in range(len(self.button_widgets_list)):
            btn_widget = self.button_widgets_list[i]
            if btn_widget.is_left_active():
                left_active_lvl = i
            if btn_widget.is_right_active():
                right_active_lvl = i
        self.sideBtnClicked.emit(left_active_lvl, right_active_lvl)


if __name__ == "__main__":
    from views import utils
    app = QtWidgets.QApplication([])
    utils.load_app_fonts()
    machine_gui_interface = DovetailSideButtons(5)
    machine_gui_interface.show()
    app.setStyleSheet(utils.load_app_style())
    app.exec_()
