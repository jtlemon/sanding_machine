# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'access_viewer_widget.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_AccessViewerWidget(object):
    def setupUi(self, AccessViewerWidget):
        if not AccessViewerWidget.objectName():
            AccessViewerWidget.setObjectName(u"AccessViewerWidget")
        AccessViewerWidget.resize(1171, 820)
        self.gridLayout = QGridLayout(AccessViewerWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.file_path_le = QLabel(AccessViewerWidget)
        self.file_path_le.setObjectName(u"file_path_le")

        self.horizontalLayout.addWidget(self.file_path_le)

        self.browse_btn = QPushButton(AccessViewerWidget)
        self.browse_btn.setObjectName(u"browse_btn")
        self.browse_btn.setMinimumSize(QSize(150, 40))

        self.horizontalLayout.addWidget(self.browse_btn)

        self.horizontalLayout.setStretch(0, 1)

        self.horizontalLayout_2.addLayout(self.horizontalLayout)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.horizontalLayout_2.setStretch(0, 2)
        self.horizontalLayout_2.setStretch(1, 6)
        self.horizontalLayout_2.setStretch(2, 2)

        self.gridLayout.addLayout(self.horizontalLayout_2, 0, 0, 1, 1)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.table_names_list_widget = QListWidget(AccessViewerWidget)
        self.table_names_list_widget.setObjectName(u"table_names_list_widget")

        self.horizontalLayout_3.addWidget(self.table_names_list_widget)

        self.scrollArea = QScrollArea(AccessViewerWidget)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 952, 748))
        self.verticalLayout = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_3)

        self.filter_btn = QPushButton(self.scrollAreaWidgetContents)
        self.filter_btn.setObjectName(u"filter_btn")
        self.filter_btn.setMinimumSize(QSize(150, 40))

        self.horizontalLayout_4.addWidget(self.filter_btn)


        self.verticalLayout.addLayout(self.horizontalLayout_4)

        self.tableWidget = QTableWidget(self.scrollAreaWidgetContents)
        self.tableWidget.setObjectName(u"tableWidget")

        self.verticalLayout.addWidget(self.tableWidget)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.horizontalLayout_3.addWidget(self.scrollArea)

        self.horizontalLayout_3.setStretch(0, 1)
        self.horizontalLayout_3.setStretch(1, 5)

        self.gridLayout.addLayout(self.horizontalLayout_3, 1, 0, 1, 1)


        self.retranslateUi(AccessViewerWidget)

        QMetaObject.connectSlotsByName(AccessViewerWidget)
    # setupUi

    def retranslateUi(self, AccessViewerWidget):
        AccessViewerWidget.setWindowTitle(QCoreApplication.translate("AccessViewerWidget", u"Form", None))
        self.file_path_le.setText(QCoreApplication.translate("AccessViewerWidget", u"path to the tld file", None))
        self.browse_btn.setText(QCoreApplication.translate("AccessViewerWidget", u"browse", None))
        self.filter_btn.setText(QCoreApplication.translate("AccessViewerWidget", u"filter", None))
    # retranslateUi

