# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'custom_widgets/two_button_combo.ui',
# licensing of 'custom_widgets/two_button_combo.ui' applies.
#
# Created: Thu Oct 29 11:39:53 2020
#      by: pyside2-uic  running on PySide2 5.13.0
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_Frame(object):
    def setupUi(self, Frame):
        Frame.setObjectName("Frame")
        Frame.resize(372, 70)
        Frame.setMaximumSize(QtCore.QSize(16777215, 70))
        Frame.setStyleSheet(".QFrame\n"
" {\n"
"     border-radius:35px;\n"
"      border-color: rgb(238, 238, 236);\n"
"      background-color: rgb(211, 215, 207);\n"
" }\n"
"QPushButton\n"
"{\n"
" \n"
"    background-color: rgb(238, 238, 236);\n"
"border-color: gray;\n"
"border-width: 1px;\n"
" border-style: solid;\n"
"border-radius:30px;\n"
"}\n"
"\n"
"QToolButton\n"
"{\n"
"    border:none;\n"
"}")
        Frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        Frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.horizontalLayout = QtWidgets.QHBoxLayout(Frame)
        self.horizontalLayout.setContentsMargins(5, 5, 5, 5)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.dec_btn = QtWidgets.QPushButton(Frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dec_btn.sizePolicy().hasHeightForWidth())
        self.dec_btn.setSizePolicy(sizePolicy)
        self.dec_btn.setMinimumSize(QtCore.QSize(120, 60))
        self.dec_btn.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        font.setFamily("Helvetica")
        font.setPointSize(18)
        font.setWeight(75)
        font.setBold(True)
        self.dec_btn.setFont(font)
        self.dec_btn.setStyleSheet("")
        self.dec_btn.setObjectName("dec_btn")
        self.horizontalLayout.addWidget(self.dec_btn)
        self.val_lbl = QtWidgets.QToolButton(Frame)
        self.val_lbl.setMinimumSize(QtCore.QSize(80, 60))
        self.val_lbl.setText("")
        self.val_lbl.setCheckable(False)
        self.val_lbl.setPopupMode(QtWidgets.QToolButton.DelayedPopup)
        self.val_lbl.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
        self.val_lbl.setAutoRaise(True)
        self.val_lbl.setObjectName("val_lbl")
        self.horizontalLayout.addWidget(self.val_lbl)
        self.unit_lbl = QtWidgets.QLabel(Frame)
        self.unit_lbl.setText("")
        self.unit_lbl.setObjectName("unit_lbl")
        self.horizontalLayout.addWidget(self.unit_lbl)
        self.extra_lbl = QtWidgets.QLabel(Frame)
        self.extra_lbl.setText("")
        self.extra_lbl.setObjectName("extra_lbl")
        self.horizontalLayout.addWidget(self.extra_lbl)
        self.inc_btn = QtWidgets.QPushButton(Frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.inc_btn.sizePolicy().hasHeightForWidth())
        self.inc_btn.setSizePolicy(sizePolicy)
        self.inc_btn.setMinimumSize(QtCore.QSize(120, 60))
        self.inc_btn.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        font.setFamily("Helvetica")
        font.setPointSize(18)
        font.setWeight(75)
        font.setBold(True)
        self.inc_btn.setFont(font)
        self.inc_btn.setStyleSheet("")
        self.inc_btn.setObjectName("inc_btn")
        self.horizontalLayout.addWidget(self.inc_btn)

        self.retranslateUi(Frame)
        QtCore.QMetaObject.connectSlotsByName(Frame)

    def retranslateUi(self, Frame):
        Frame.setWindowTitle(QtWidgets.QApplication.translate("Frame", "Frame", None, -1))
        self.dec_btn.setText(QtWidgets.QApplication.translate("Frame", "Left ", None, -1))
        self.inc_btn.setText(QtWidgets.QApplication.translate("Frame", "Right", None, -1))

