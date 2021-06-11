from PySide2 import QtCore, QtWidgets, QtGui


class AlarmViewerDialog(QtWidgets.QDialog):
    def __init__(self, all_alarms, parent):
        super(AlarmViewerDialog, self).__init__(parent=parent)
        self.widget_layout = QtWidgets.QVBoxLayout(self)
        self.all_alarms_browser = QtWidgets.QTextBrowser()
        self.widget_layout.addWidget(self.all_alarms_browser)
        self.reset_btn = QtWidgets.QPushButton("Clear Alarms")
        self.reset_btn.setFixedSize(200, 60)
        self.widget_layout.addWidget(self.reset_btn, alignment=QtCore.Qt.AlignCenter)
        self.reset_btn.clicked.connect(self.accept)
        # load alarms
        for error_key, error_text, color in all_alarms:
            self.all_alarms_browser.setTextColor(QtGui.QColor(color))
            self.all_alarms_browser.append(f"{error_key} - {error_text}")
        self.setMinimumSize(700, 400)
        self.adjustSize()



