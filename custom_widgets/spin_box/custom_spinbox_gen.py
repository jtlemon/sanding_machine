# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'custom_widgets/custom_spinbox.ui'
#
# Created by: PyQt5 UI code generator 5.14.0
#
# WARNING! All changes made in this file will be lost!


from PySide2 import QtCore, QtGui, QtWidgets


class Ui_Frame(object):
    def setupUi(self, Frame):
        Frame.setObjectName("Frame")
        Frame.resize(219, 100)
        Frame.setMinimumSize(QtCore.QSize(0, 100))
        Frame.setStyleSheet("QFrame\n"
"{\n"
"     border-radius:50px;\n"
"    border-color: rgb(238, 238, 236);\n"
"    \n"
"}\n"
"QWidget\n"
"{\n"
"    \n"
"    background-color: rgb(211, 215, 207);\n"
"}\n"
"\n"
"QToolButton\n"
"{\n"
"    /*border:none;*/\n"
"   border:none;\n"
"  border-radius:25px;\n"
"   \n"
"}\n"
"QToolButton:pressed\n"
"{\n"
"    /*border:none;*/\n"
"   border:2px solid rgb(255,255,255);\n"
"    background-color: rgb(255, 255, 255);\n"
"  border-radius:25px;\n"
"   \n"
"}\n"
"QLabel\n"
"{\n"
"   font-size:18px;\n"
"}")
        self.horizontalLayout = QtWidgets.QHBoxLayout(Frame)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.dec_btn = QtWidgets.QToolButton(Frame)
        self.dec_btn.setMinimumSize(QtCore.QSize(50, 50))
        self.dec_btn.setMaximumSize(QtCore.QSize(50, 50))
        self.dec_btn.setStyleSheet("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/icons/icons8-minus-96.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.dec_btn.setIcon(icon)
        self.dec_btn.setIconSize(QtCore.QSize(25, 25))
        self.dec_btn.setAutoRaise(False)
        self.dec_btn.setObjectName("dec_btn")
        self.horizontalLayout.addWidget(self.dec_btn)
        spacerItem = QtWidgets.QSpacerItem(0, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.val_lbl = QtWidgets.QLabel(Frame)
        self.val_lbl.setMinimumSize(QtCore.QSize(40, 0))
        self.val_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.val_lbl.setObjectName("val_lbl")
        self.horizontalLayout.addWidget(self.val_lbl)
        self.unit_lbl = QtWidgets.QLabel(Frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.unit_lbl.sizePolicy().hasHeightForWidth())
        self.unit_lbl.setSizePolicy(sizePolicy)
        self.unit_lbl.setObjectName("unit_lbl")
        self.horizontalLayout.addWidget(self.unit_lbl)
        self.extra_lbl = QtWidgets.QLabel(Frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.extra_lbl.sizePolicy().hasHeightForWidth())
        self.extra_lbl.setSizePolicy(sizePolicy)
        self.extra_lbl.setText("")
        self.extra_lbl.setObjectName("extra_lbl")
        self.horizontalLayout.addWidget(self.extra_lbl)
        spacerItem1 = QtWidgets.QSpacerItem(0, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.inc_btn = QtWidgets.QToolButton(Frame)
        self.inc_btn.setMinimumSize(QtCore.QSize(50, 50))
        self.inc_btn.setMaximumSize(QtCore.QSize(50, 50))
        self.inc_btn.setStyleSheet("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/icons/icons8-plus-144.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.inc_btn.setIcon(icon1)
        self.inc_btn.setIconSize(QtCore.QSize(25, 25))
        self.inc_btn.setAutoRaise(True)
        self.inc_btn.setArrowType(QtCore.Qt.NoArrow)
        self.inc_btn.setObjectName("inc_btn")
        self.horizontalLayout.addWidget(self.inc_btn)

        self.retranslateUi(Frame)
        QtCore.QMetaObject.connectSlotsByName(Frame)

    def retranslateUi(self, Frame):
        _translate = QtCore.QCoreApplication.translate
        Frame.setWindowTitle(_translate("Frame", "Frame"))
        self.dec_btn.setText(_translate("Frame", "..."))
        self.val_lbl.setText(_translate("Frame", "0.0"))
        self.unit_lbl.setText(_translate("Frame", "mm"))
        self.inc_btn.setText(_translate("Frame", "..."))

import app_resources_rc
