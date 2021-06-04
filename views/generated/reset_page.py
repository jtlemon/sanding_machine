# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'reset_page.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_ResetPage(object):
    def setupUi(self, ResetPage):
        if not ResetPage.objectName():
            ResetPage.setObjectName(u"ResetPage")
        ResetPage.resize(1017, 589)
        self.verticalLayout = QVBoxLayout(ResetPage)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, -1, 0, -1)
        self.control_frame = QFrame(ResetPage)
        self.control_frame.setObjectName(u"control_frame")
        self.control_frame.setFrameShape(QFrame.StyledPanel)
        self.control_frame.setFrameShadow(QFrame.Raised)

        self.verticalLayout.addWidget(self.control_frame)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.camera_frame = QFrame(ResetPage)
        self.camera_frame.setObjectName(u"camera_frame")
        self.camera_frame.setFrameShape(QFrame.StyledPanel)
        self.camera_frame.setFrameShadow(QFrame.Raised)

        self.horizontalLayout.addWidget(self.camera_frame)

        self.serial_monitor_frame = QFrame(ResetPage)
        self.serial_monitor_frame.setObjectName(u"serial_monitor_frame")
        self.serial_monitor_frame.setFrameShape(QFrame.StyledPanel)
        self.serial_monitor_frame.setFrameShadow(QFrame.Raised)

        self.horizontalLayout.addWidget(self.serial_monitor_frame)

        self.horizontalLayout.setStretch(0, 5)
        self.horizontalLayout.setStretch(1, 2)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.verticalLayout.setStretch(0, 1)
        self.verticalLayout.setStretch(1, 4)

        self.retranslateUi(ResetPage)

        QMetaObject.connectSlotsByName(ResetPage)
    # setupUi

    def retranslateUi(self, ResetPage):
        ResetPage.setWindowTitle(QCoreApplication.translate("ResetPage", u"Form", None))
    # retranslateUi

