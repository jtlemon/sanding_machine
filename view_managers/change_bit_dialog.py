from PySide2 import QtCore, QtWidgets
from apps.bit_profiles.models import BitProfile
from views.spinner import  WaitingSpinner

class ChangeBitDialog(QtWidgets.QDialog):
    callMeasureToolSignal = QtCore.Signal()
    def __init__(self,time_out_ms = 5000, parent=None):
        super(ChangeBitDialog, self).__init__(parent= parent)
        self.__time_out_ms = time_out_ms
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.FramelessWindowHint)
        self.dialog_layout = QtWidgets.QVBoxLayout(self)
        self.header_label = QtWidgets.QLabel("Bit Profile")
        self.bit_profile_objects = BitProfile.objects.all()
        bit_profile_names = [bit_profile.profile_name for bit_profile in self.bit_profile_objects]
        self.bit_combo_box = QtWidgets.QComboBox()
        self.bit_combo_box.addItems(bit_profile_names)
        self.bit_combo_box.setMinimumWidth(240)
        h_spacer_1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.profile_layout = QtWidgets.QHBoxLayout()
        self.profile_layout.addItem(h_spacer_1)
        self.profile_layout.addWidget(self.header_label)
        self.profile_layout.addWidget(self.bit_combo_box)
        h_spacer_2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.profile_layout.addItem(h_spacer_2)

        self.close_btn = QtWidgets.QPushButton("Close")
        self.close_btn.setFixedSize(150, 60)
        self.load_btn = QtWidgets.QPushButton("Load")
        self.load_btn.setFixedSize(150, 60)
        h_spacer_3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        h_spacer_4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.footer_buttons_layout = QtWidgets.QHBoxLayout()
        self.footer_buttons_layout.addItem(h_spacer_3)
        self.footer_buttons_layout.addWidget(self.close_btn)
        self.footer_buttons_layout.addWidget(self.load_btn)
        self.footer_buttons_layout.addItem(h_spacer_4)
        self.dialog_layout.addLayout(self.profile_layout)

        self.footer_error_lbl = QtWidgets.QLabel("the dialog will close automatically after the process complete")
        self.footer_error_lbl.setObjectName("bit_dialog_footer_error_lbl")
        self.footer_error_lbl.setWordWrap(True)
        self.footer_error_lbl.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        self.footer_error_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.dialog_layout.addWidget(self.footer_error_lbl)
        self.dialog_layout.addLayout(self.footer_buttons_layout)

        self.close_btn.clicked.connect(self.reject)
        self.load_btn.clicked.connect(self.handle_load_bit)
        self.spinner_widget = WaitingSpinner(self)
        self.param_retrieve_fail_timer = QtCore.QTimer()
        self.param_retrieve_fail_timer.setSingleShot(True)
        self.param_retrieve_fail_timer.setInterval(time_out_ms)
        self.param_retrieve_fail_timer.timeout.connect(self.handle_time_out)
        self.footer_error_lbl.show()
        self.footer_error_lbl.hide()
        self.setMinimumHeight(160)


    def handle_time_out(self):
        self.footer_error_lbl.setText("Timeout Failed to retrieve the Values")
        self.footer_error_lbl.show()
        self.spinner_widget.stop()
    def handle_load_bit(self):
        self.callMeasureToolSignal.emit()
        self.spinner_widget.start()
        self.param_retrieve_fail_timer.start()
        self.footer_error_lbl.setText("the dialog will close automatically after the process complete")
        self.footer_error_lbl.show()

    def get_selected_bit_profile(self):
        bit_profile_index = self.bit_combo_box.currentIndex()
        return self.bit_profile_objects[bit_profile_index]



