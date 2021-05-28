# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'dovetail_camera_page.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from views.custom_app_widgets import ProfileComboBox

import app_resources_rc

class Ui_DovetailCameraPageUI(object):
    def setupUi(self, DovetailCameraPageUI):
        if not DovetailCameraPageUI.objectName():
            DovetailCameraPageUI.setObjectName(u"DovetailCameraPageUI")
        DovetailCameraPageUI.resize(1014, 668)
        DovetailCameraPageUI.setStyleSheet(u"")
        self.horizontalLayout_4 = QHBoxLayout(DovetailCameraPageUI)
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.sidebar_frame = QFrame(DovetailCameraPageUI)
        self.sidebar_frame.setObjectName(u"sidebar_frame")
        self.sidebar_frame.setFrameShape(QFrame.StyledPanel)
        self.sidebar_frame.setFrameShadow(QFrame.Raised)

        self.horizontalLayout_4.addWidget(self.sidebar_frame)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(12)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_12 = QHBoxLayout()
        self.horizontalLayout_12.setSpacing(40)
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.horizontalLayout_12.setContentsMargins(-1, 12, -1, -1)
        self.horizontalSpacer_29 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_12.addItem(self.horizontalSpacer_29)

        self.start_button = QPushButton(DovetailCameraPageUI)
        self.start_button.setObjectName(u"start_button")
        self.start_button.setMinimumSize(QSize(200, 75))
        font = QFont()
        font.setFamily(u"Helvetica")
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.start_button.setFont(font)
        self.start_button.setStyleSheet(u"")

        self.horizontalLayout_12.addWidget(self.start_button)

        self.cancel_Button = QPushButton(DovetailCameraPageUI)
        self.cancel_Button.setObjectName(u"cancel_Button")
        self.cancel_Button.setMinimumSize(QSize(200, 75))
        self.cancel_Button.setFont(font)

        self.horizontalLayout_12.addWidget(self.cancel_Button)

        self.horizontalSpacer_27 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_12.addItem(self.horizontalSpacer_27)


        self.verticalLayout.addLayout(self.horizontalLayout_12)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalSpacer_6 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_6)

        self.label_12 = QLabel(DovetailCameraPageUI)
        self.label_12.setObjectName(u"label_12")

        self.horizontalLayout_3.addWidget(self.label_12)

        self.available_profiles_combo = ProfileComboBox(DovetailCameraPageUI)
        self.available_profiles_combo.setObjectName(u"available_profiles_combo")
        self.available_profiles_combo.setMinimumSize(QSize(150, 60))

        self.horizontalLayout_3.addWidget(self.available_profiles_combo)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_3)


        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.camera_display = QLabel(DovetailCameraPageUI)
        self.camera_display.setObjectName(u"camera_display")
        self.camera_display.setMinimumSize(QSize(720, 420))
        self.camera_display.setMaximumSize(QSize(720, 400))
        self.camera_display.setPixmap(QPixmap(u":/icons/icons/icons8-camera-96.png"))
        self.camera_display.setScaledContents(True)
        self.camera_display.setAlignment(Qt.AlignCenter)

        self.horizontalLayout.addWidget(self.camera_display)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer_2)

        self.verticalLayout.setStretch(4, 1)

        self.horizontalLayout_4.addLayout(self.verticalLayout)

        self.horizontalLayout_4.setStretch(0, 3)
        self.horizontalLayout_4.setStretch(1, 7)

        self.retranslateUi(DovetailCameraPageUI)

        QMetaObject.connectSlotsByName(DovetailCameraPageUI)
    # setupUi

    def retranslateUi(self, DovetailCameraPageUI):
        DovetailCameraPageUI.setWindowTitle(QCoreApplication.translate("DovetailCameraPageUI", u"Form", None))
        self.start_button.setText(QCoreApplication.translate("DovetailCameraPageUI", u"Start", None))
        self.cancel_Button.setText(QCoreApplication.translate("DovetailCameraPageUI", u"Cancel", None))
        self.label_12.setText(QCoreApplication.translate("DovetailCameraPageUI", u"Joint type ", None))
        self.camera_display.setText("")
    # retranslateUi

