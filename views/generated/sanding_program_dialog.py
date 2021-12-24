# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'sanding_program_dialog.ui'
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

class Ui_SandingProgramCreationDialog(object):
    def setupUi(self, SandingProgramCreationDialog):
        if not SandingProgramCreationDialog.objectName():
            SandingProgramCreationDialog.setObjectName(u"SandingProgramCreationDialog")
        SandingProgramCreationDialog.resize(939, 495)
        SandingProgramCreationDialog.setStyleSheet(u"")
        self.gridLayout = QGridLayout(SandingProgramCreationDialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(-1, 0, -1, -1)
        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_3)

        self.save_update_btn = QPushButton(SandingProgramCreationDialog)
        self.save_update_btn.setObjectName(u"save_update_btn")
        self.save_update_btn.setMinimumSize(QSize(200, 60))

        self.horizontalLayout_3.addWidget(self.save_update_btn)


        self.gridLayout.addLayout(self.horizontalLayout_3, 3, 1, 1, 1)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.passes_list = QListWidget(SandingProgramCreationDialog)
        __qlistwidgetitem = QListWidgetItem(self.passes_list)
        __qlistwidgetitem.setFlags(Qt.ItemIsSelectable|Qt.ItemIsEditable|Qt.ItemIsDragEnabled|Qt.ItemIsUserCheckable|Qt.ItemIsEnabled);
        self.passes_list.setObjectName(u"passes_list")

        self.verticalLayout.addWidget(self.passes_list)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.del_pass_btn = QToolButton(SandingProgramCreationDialog)
        self.del_pass_btn.setObjectName(u"del_pass_btn")
        icon = QIcon()
        icon.addFile(u":/icons/icons/icons8-delete-bin-96.png", QSize(), QIcon.Normal, QIcon.Off)
        self.del_pass_btn.setIcon(icon)
        self.del_pass_btn.setIconSize(QSize(20, 20))

        self.horizontalLayout.addWidget(self.del_pass_btn)

        self.add_pass_btn = QToolButton(SandingProgramCreationDialog)
        self.add_pass_btn.setObjectName(u"add_pass_btn")
        icon1 = QIcon()
        icon1.addFile(u":/icons/icons/icons8-plus-144.png", QSize(), QIcon.Normal, QIcon.Off)
        self.add_pass_btn.setIcon(icon1)
        self.add_pass_btn.setIconSize(QSize(20, 20))

        self.horizontalLayout.addWidget(self.add_pass_btn)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.gridLayout.addLayout(self.verticalLayout, 1, 0, 1, 1)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label = QLabel(SandingProgramCreationDialog)
        self.label.setObjectName(u"label")

        self.horizontalLayout_2.addWidget(self.label)

        self.program_name_lin = QLineEdit(SandingProgramCreationDialog)
        self.program_name_lin.setObjectName(u"program_name_lin")

        self.horizontalLayout_2.addWidget(self.program_name_lin)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)


        self.gridLayout.addLayout(self.horizontalLayout_2, 0, 0, 1, 2)

        self.stackedWidget = QStackedWidget(SandingProgramCreationDialog)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.page = QWidget()
        self.page.setObjectName(u"page")
        self.stackedWidget.addWidget(self.page)
        self.page_2 = QWidget()
        self.page_2.setObjectName(u"page_2")
        self.verticalLayout_3 = QVBoxLayout(self.page_2)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_2 = QLabel(self.page_2)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout_4.addWidget(self.label_2)

        self.sanders_combo_box = ProfileComboBox(self.page_2)
        self.sanders_combo_box.setObjectName(u"sanders_combo_box")
        self.sanders_combo_box.setMinimumSize(QSize(250, 60))
        self.sanders_combo_box.setMaximumSize(QSize(250, 16777215))

        self.horizontalLayout_4.addWidget(self.sanders_combo_box)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_4)

        self.label_3 = QLabel(self.page_2)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout_4.addWidget(self.label_3)

        self.grit_combobox = ProfileComboBox(self.page_2)
        self.grit_combobox.setObjectName(u"grit_combobox")
        self.grit_combobox.setMinimumSize(QSize(250, 60))
        self.grit_combobox.setMaximumSize(QSize(250, 16777215))

        self.horizontalLayout_4.addWidget(self.grit_combobox)


        self.verticalLayout_3.addLayout(self.horizontalLayout_4)

        self.frame = QFrame(self.page_2)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.frame)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.checkBox = QCheckBox(self.frame)
        self.checkBox.setObjectName(u"checkBox")

        self.verticalLayout_2.addWidget(self.checkBox)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.panels_checkbox = QCheckBox(self.frame)
        self.panels_checkbox.setObjectName(u"panels_checkbox")

        self.horizontalLayout_5.addWidget(self.panels_checkbox)

        self.panel_option_frame = QFrame(self.frame)
        self.panel_option_frame.setObjectName(u"panel_option_frame")
        self.panel_option_frame.setFrameShape(QFrame.NoFrame)
        self.panel_option_frame.setFrameShadow(QFrame.Raised)
        self.gridLayout_2 = QGridLayout(self.panel_option_frame)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.radioButton_2 = QRadioButton(self.panel_option_frame)
        self.radioButton_2.setObjectName(u"radioButton_2")

        self.gridLayout_2.addWidget(self.radioButton_2, 0, 1, 1, 1)

        self.radioButton = QRadioButton(self.panel_option_frame)
        self.radioButton.setObjectName(u"radioButton")

        self.gridLayout_2.addWidget(self.radioButton, 0, 0, 1, 1)

        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout_2.addItem(self.horizontalSpacer_5, 0, 2, 1, 1)


        self.horizontalLayout_5.addWidget(self.panel_option_frame)


        self.verticalLayout_2.addLayout(self.horizontalLayout_5)

        self.slabs_checkbox = QCheckBox(self.frame)
        self.slabs_checkbox.setObjectName(u"slabs_checkbox")

        self.verticalLayout_2.addWidget(self.slabs_checkbox)

        self.extra_pass_around_perimeter_checkbox = QCheckBox(self.frame)
        self.extra_pass_around_perimeter_checkbox.setObjectName(u"extra_pass_around_perimeter_checkbox")

        self.verticalLayout_2.addWidget(self.extra_pass_around_perimeter_checkbox)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.custom_prams_grid = QGridLayout()
        self.custom_prams_grid.setObjectName(u"custom_prams_grid")
        self.label_4 = QLabel(self.frame)
        self.label_4.setObjectName(u"label_4")

        self.custom_prams_grid.addWidget(self.label_4, 1, 0, 1, 1)

        self.label_6 = QLabel(self.frame)
        self.label_6.setObjectName(u"label_6")

        self.custom_prams_grid.addWidget(self.label_6, 2, 0, 1, 1)

        self.label_7 = QLabel(self.frame)
        self.label_7.setObjectName(u"label_7")

        self.custom_prams_grid.addWidget(self.label_7, 3, 0, 1, 1)

        self.label_5 = QLabel(self.frame)
        self.label_5.setObjectName(u"label_5")

        self.custom_prams_grid.addWidget(self.label_5, 0, 0, 1, 1)


        self.horizontalLayout_6.addLayout(self.custom_prams_grid)

        self.horizontalSpacer_6 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_6)


        self.verticalLayout_2.addLayout(self.horizontalLayout_6)


        self.verticalLayout_3.addWidget(self.frame)

        self.stackedWidget.addWidget(self.page_2)

        self.gridLayout.addWidget(self.stackedWidget, 1, 1, 1, 1)

        self.gridLayout.setColumnStretch(1, 1)

        self.retranslateUi(SandingProgramCreationDialog)

        self.stackedWidget.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(SandingProgramCreationDialog)
    # setupUi

    def retranslateUi(self, SandingProgramCreationDialog):
        SandingProgramCreationDialog.setWindowTitle(QCoreApplication.translate("SandingProgramCreationDialog", u"Create/Edit Sanding program", None))
        self.save_update_btn.setText(QCoreApplication.translate("SandingProgramCreationDialog", u"Save/Update", None))

        __sortingEnabled = self.passes_list.isSortingEnabled()
        self.passes_list.setSortingEnabled(False)
        ___qlistwidgetitem = self.passes_list.item(0)
        ___qlistwidgetitem.setText(QCoreApplication.translate("SandingProgramCreationDialog", u"New Item", None));
        self.passes_list.setSortingEnabled(__sortingEnabled)

        self.del_pass_btn.setText(QCoreApplication.translate("SandingProgramCreationDialog", u"...", None))
        self.add_pass_btn.setText(QCoreApplication.translate("SandingProgramCreationDialog", u"...", None))
        self.label.setText(QCoreApplication.translate("SandingProgramCreationDialog", u"Name", None))
        self.program_name_lin.setPlaceholderText(QCoreApplication.translate("SandingProgramCreationDialog", u"program name ", None))
        self.label_2.setText(QCoreApplication.translate("SandingProgramCreationDialog", u"Sander", None))
        self.label_3.setText(QCoreApplication.translate("SandingProgramCreationDialog", u"grit", None))
        self.checkBox.setText(QCoreApplication.translate("SandingProgramCreationDialog", u"Frames", None))
        self.panels_checkbox.setText(QCoreApplication.translate("SandingProgramCreationDialog", u"panels", None))
        self.radioButton_2.setText(QCoreApplication.translate("SandingProgramCreationDialog", u" only perimeter", None))
        self.radioButton.setText(QCoreApplication.translate("SandingProgramCreationDialog", u"entire panel ", None))
        self.slabs_checkbox.setText(QCoreApplication.translate("SandingProgramCreationDialog", u"slabs", None))
        self.extra_pass_around_perimeter_checkbox.setText(QCoreApplication.translate("SandingProgramCreationDialog", u"Make extra pass around perimeter", None))
        self.label_4.setText(QCoreApplication.translate("SandingProgramCreationDialog", u"pressure", None))
        self.label_6.setText(QCoreApplication.translate("SandingProgramCreationDialog", u"Speed", None))
        self.label_7.setText(QCoreApplication.translate("SandingProgramCreationDialog", u"Hangover", None))
        self.label_5.setText(QCoreApplication.translate("SandingProgramCreationDialog", u"Overlap", None))
    # retranslateUi

