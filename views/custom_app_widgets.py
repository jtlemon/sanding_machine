from PySide2 import QtWidgets, QtCore, QtGui


class RecordTrackBtn(QtWidgets.QPushButton):
    customClickSignal = QtCore.Signal(int)

    def __init__(self, record_id, icon_path=None):
        super(RecordTrackBtn, self).__init__()
        self.__current_id = record_id
        if icon_path:
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(icon_path), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.setIcon(icon)
            self.setIconSize(QtCore.QSize(30, 30))
        self.clicked.connect(lambda: self.customClickSignal.emit(record_id))

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
        self.action_combo_btn.clicked.connect(lambda: self.combo_box.showPopup())
        self.combo_box.currentTextChanged.connect(lambda txt: self.currentTextChanged.emit(txt))

    def addItems(self, items):
        self.combo_box.addItems(items)

    def clear(self):
        self.combo_box.clear()

    def currentIndex(self):
        return self.combo_box.currentIndex()

    def currentText(self):
        return self.combo_box.currentText()

    def setCurrentIndex(self, index):
        self.combo_box.setCurrentIndex(index)

    def setCurrentText(self, text):
        self.combo_box.setCurrentText(text)

    def set_default_option(self, default):
        index = self.combo_box.findText(default)
        self.combo_box.setCurrentIndex(index)

    def load_new_options(self, options):
        current_option = self.combo_box.currentText()
        self.combo_box.clear()
        self.combo_box.addItems(options)
        target_index = self.combo_box.findText(current_option)
        self.combo_box.setCurrentIndex(target_index)


class SaveCancelButtons(QtWidgets.QWidget):
    def __init__(self):
        super(SaveCancelButtons, self).__init__()
        # save/cancel buttons
        self.save_btn = QtWidgets.QPushButton("Save")
        self.save_btn.setMinimumSize(200, 60)
        self.cancel_btn = QtWidgets.QPushButton("Cancel")
        self.cancel_btn.setMinimumSize(200, 60)
        self.footer_layout = QtWidgets.QHBoxLayout(self)
        h_spacer_item_1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding,
                                                QtWidgets.QSizePolicy.Preferred)
        h_spacer_item_2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding,
                                                QtWidgets.QSizePolicy.Preferred)
        self.footer_layout.addItem(h_spacer_item_1)
        self.footer_layout.addWidget(self.cancel_btn)
        self.footer_layout.addWidget(self.save_btn)
        self.footer_layout.addItem(h_spacer_item_2)


class QLineEditWithSideLabel(QtWidgets.QWidget):
    def __init__(self, lbl_txt, line_text=""):
        super(QLineEditWithSideLabel, self).__init__()
        self.widget_layout = QtWidgets.QHBoxLayout(self)
        self.widget_lbl = QtWidgets.QLabel(lbl_txt)
        self.text_edit_widget = QtWidgets.QLineEdit(line_text)
        self.widget_layout.addWidget(self.widget_lbl, stretch=0)
        self.widget_layout.addWidget(self.text_edit_widget, stretch=1)
        h_spacer_item_1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding,
                                                QtWidgets.QSizePolicy.Preferred)
        self.widget_layout.addItem(h_spacer_item_1)

    def setText(self, text):
        self.text_edit_widget.setText(text)

    def text(self):
        return self.text_edit_widget.text()


class CenterPagePushButton(QtWidgets.QWidget):
    def __init__(self, btn_text="", icon_path=None):
        super(CenterPagePushButton, self).__init__()
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.widget_layout = QtWidgets.QHBoxLayout(self)
        h_spacer_item_1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding,
                                                QtWidgets.QSizePolicy.Preferred)
        self.widget_layout.addItem(h_spacer_item_1)
        self.widget_btn = QtWidgets.QPushButton(btn_text)
        self.widget_layout.addWidget(self.widget_btn)
        self.widget_btn.setObjectName("center_btn_widget")
        if icon_path:
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(icon_path), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.widget_btn.setIcon(icon)
            self.widget_btn.setIconSize(QtCore.QSize(30, 30))
        h_spacer_item_2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding,
                                                QtWidgets.QSizePolicy.Preferred)
        self.widget_layout.addItem(h_spacer_item_2)
        self.clicked = self.widget_btn.clicked

class TrackableCheckBox(QtWidgets.QCheckBox):
    def __init__(self, *args, key_name, **kwargs):
        super(TrackableCheckBox, self).__init__(*args, **kwargs)
        self.__key_name = key_name

    def get_key(self):
        return self.__key_name

    def set_value(self, new_value):
        self.setChecked(True if new_value else False)

    def value(self):
        return self.isChecked()
