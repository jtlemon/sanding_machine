from PySide2 import QtWidgets, QtCore, QtGui

class RecordTrackBtn(QtWidgets.QPushButton):
    customClickSignal = QtCore.Signal(int)
    def __init__(self, record_id,icon_path=None):
        super(RecordTrackBtn, self).__init__()
        self.__current_id = record_id
        if icon_path:
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(icon_path), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.setIcon(icon)
            self.setIconSize(QtCore.QSize(30, 30))
        self.clicked.connect(lambda :self.customClickSignal.emit(record_id))

    def get_id(self):
        return self.__current_id


class AppFooterButton(QtWidgets.QPushButton):
    customClickSignal = QtCore.Signal(int)

    def __init__(self, *args, target_page=-1, **kwargs):
        super(AppFooterButton, self).__init__(*args, **kwargs)
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.clicked.connect(lambda: self.customClickSignal.emit(target_page))


class ProfileComboBox(QtWidgets.QWidget):
    currentTextChanged = QtCore.Signal(str)
    def __init__(self, parent):
        super(ProfileComboBox, self).__init__(parent=parent)
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.widget_layout = QtWidgets.QHBoxLayout(self)
        self.widget_layout.setSpacing(0)
        self.combo_box = QtWidgets.QComboBox()
        self.widget_layout.addWidget(self.combo_box, stretch=1)
        self.action_combo_btn = QtWidgets.QPushButton()
        self.action_combo_btn.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        self.action_combo_btn.setObjectName("action_combo_btn")
        self.action_combo_btn.setIconSize(QtCore.QSize(35, 35))
        self.widget_layout.addWidget(self.action_combo_btn, stretch=0)
        self.setMinimumHeight(50)
        self.combo_box.addItems(["hello", "world", "hey", "there"])
        self.action_combo_btn.clicked.connect(lambda: self.combo_box.showPopup())
        self.combo_box.currentTextChanged.connect(lambda txt: self.currentTextChanged.emit(txt))

    def addItems(self, items):
        self.combo_box.addItems(items)

    def clear(self):
        self.combo_box.clear()

    def currentIndex(self):
        return self.combo_box.currentIndex()

    def currentText(self):
        return  self.combo_box.currentText()




