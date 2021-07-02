import json
import os
import time

import serial
import serial.tools.list_ports
from PySide2 import QtCore, QtWidgets, QtGui
from views.spinner import  WaitingSpinner
from view_managers.utils import add_item_to_table

CONFIGURATION_FILE_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "configurations",
                                       "machine_prams.json")

import configurations.static_app_configurations as static_configurations

NAMES_MAPPER = \
    {
        "$0": "step_pulse_usec",
        "$1": "step_idle_delay_msec",
        "$2": "step_port_invert_mask",
        "$3": "dir_port_invert_mask",
        "$4": "step_enable_invert_bool",
        "$5": "limit_pins_invert_bool",
        "$6": "probe_pin_invert_bool",
        "$10": "status_report_mask",
        "$11": "junction_deviation_mm",
        "$12": "arc_tolerance_mm",
        "$13": "report_inches_bool",
        "$20": "soft_limits_bool",
        "$21": "hard_limits_bool",
        "$22": "homing_cycle_bool",
        "$23": "homing_dir_invert_mask",
        "$24": "homing_feed_mm_by_min",
        "$25": "homing_seek_mm_by_min",
        "$26": "homing_debounce_msec",
        "$27": "homing_pull-off_mm",
        "$100": "x_step_by_mm",
        "$101": "y_step_by_mm",
        "$102": "z_step_by_mm",
        "$103": "a_step_by_mm",
        "$104": "b_step_by_mm",
        "$110": "x_max_rate_mm_by_min",
        "$111": "y_max_rate_mm_by_min",
        "$112": "z_max_rate_mm_by_min",
        "$113": "a_max_rate_mm_by_min",
        "$114": "b_max_rate_mm_by_min",
        "$120": "x_accel_mm_by_sec_2",
        "$121": "y_accel_mm_by_sec_2",
        "$122": "z_accel_mm_by_sec_2",
        "$123": "a_accel_mm_by_sec_2",
        "$124": "b_accel_mm_by_sec_2",

        "$130": "x_max_travel_mm",
        "$131": "y_max_travel_mm",
        "$132": "z_max_travel_mm",
        "$133": "a_max_travel_mm",
        "$134": "b_max_travel_mm"
    }


class ScanningThread(QtCore.QThread):
    def __init__(self):
        super(ScanningThread, self).__init__()
        self.__machine_prams = dict()
        self.__last_error = "Unknown Error"

    def run(self):
        time.sleep(1)
        serial_dev = None
        available_ports = [port.device for port in serial.tools.list_ports.comports()]
        if static_configurations.GRBL_MODULE_COM_PORT not in available_ports:
            self.__last_error = "Board Not Connected."
            print("thread end.........")
            return
        try:
            serial_dev = serial.Serial(static_configurations.GRBL_MODULE_COM_PORT,
            115200, timeout=4)
            while not serial_dev.isOpen():
                time.sleep(0.1)
            time.sleep(1)
            serial_dev.write(b"$")
            serial_dev.write(b"\n")
            serial_dev.flush()
            time.sleep(0.2)
            available_bytes = serial_dev.read(200)
            if b"ok" in available_bytes:
                serial_dev.flush()
                serial_dev.write(b"$$\n")
                lines = serial_dev.read_until(b"ok")
                lines_str = lines.decode()
                self.__machine_prams = {}
                for pram in lines_str.split("\r\n"):
                    name_val = pram.split("=")
                    if len(name_val) == 2:
                        pram_name = NAMES_MAPPER.get(name_val[0], name_val[0])
                        self.__machine_prams[pram_name] = float(name_val[1])

        except Exception as e:
            print(e)
        finally:
            if serial_dev:
                serial_dev.close()


    def get_machine_prams(self):
        return self.__machine_prams

    def get_latest_error(self):
        return self.__last_error


class RetrieveMachinePramsDialog(QtWidgets.QDialog):
    def __init__(self):
        super(RetrieveMachinePramsDialog, self).__init__()
        self.widget_layout = QtWidgets.QGridLayout(self)
        # loading prams widget
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.loading_prams_widget = QtWidgets.QWidget()
        self.loading_prams_layout = QtWidgets.QVBoxLayout(self.loading_prams_widget)
        self.spinner_widget = WaitingSpinner(self.loading_prams_widget)
        self.loading_prams_layout.addWidget(self.spinner_widget)
        self.loading_prams_lbl = QtWidgets.QLabel("Please Wait while retrieving the machine parameters.")
        self.loading_prams_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.loading_prams_layout.addWidget(self.loading_prams_lbl)
        self.footer_btn_frame = QtWidgets.QFrame()
        self.footer_btn_frame_layout = QtWidgets.QVBoxLayout(self.footer_btn_frame)
        self.try_again_btn = QtWidgets.QPushButton("try again")
        self.try_again_btn.setFixedSize(200, 60)
        self.start_program_btn = QtWidgets.QPushButton("Start")
        self.start_program_btn.setFixedSize(200, 60)
        self.close_program_btn = QtWidgets.QPushButton("Close")
        self.close_program_btn.setFixedSize(200, 60)
        self.footer_btn_frame_layout.addWidget(self.try_again_btn, alignment=QtCore.Qt.AlignCenter)
        self.footer_btn_frame_layout.addWidget(self.start_program_btn, alignment=QtCore.Qt.AlignCenter)
        self.footer_btn_frame_layout.addWidget(self.close_program_btn, alignment=QtCore.Qt.AlignCenter)
        self.loading_prams_layout.addWidget(self.footer_btn_frame)
        self.footer_btn_frame.setVisible(False)
        # machine prams changed
        self.machine_prams_widget = QtWidgets.QWidget()
        self.machine_prams_layout = QtWidgets.QVBoxLayout(self.machine_prams_widget)
        self.machine_prams_table = QtWidgets.QTableWidget()
        col_names = ["Pram", "Old Value", "New Value"]
        self.machine_prams_table.setColumnCount(len(col_names))
        self.machine_prams_table.setHorizontalHeaderLabels(col_names)
        for i in range(self.machine_prams_table.columnCount()):
            self.machine_prams_table.horizontalHeader().setSectionResizeMode(i, QtWidgets.QHeaderView.Stretch)

        self.changes_footer_frame = QtWidgets.QFrame()
        self.footer_layout = QtWidgets.QHBoxLayout(self.changes_footer_frame)
        self.accept_btn = QtWidgets.QPushButton("Accept New Changes")
        self.accept_btn.setFixedSize(300, 60)
        self.close_machine_btn = QtWidgets.QPushButton("Close")
        self.close_machine_btn.setFixedSize(300, 60)
        self.keep_old_btn = QtWidgets.QPushButton("Keep Old")
        self.keep_old_btn.setFixedSize(300, 60)
        self.footer_layout.addWidget(self.keep_old_btn, alignment=QtCore.Qt.AlignCenter)
        self.footer_layout.addWidget(self.close_machine_btn, alignment=QtCore.Qt.AlignCenter)
        self.footer_layout.addWidget(self.accept_btn, alignment=QtCore.Qt.AlignCenter)
        self.machine_prams_layout.addWidget(self.machine_prams_table)
        self.machine_prams_layout.addWidget(self.changes_footer_frame)
        # no changes
        self.no_changes_footer_frame = QtWidgets.QFrame()
        self.no_changes_footer_layout = QtWidgets.QVBoxLayout(self.no_changes_footer_frame)
        self.no_changes_lbl = QtWidgets.QLabel("No Changes detected")
        self.no_changes_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.no_changes_footer_layout.addWidget(self.no_changes_lbl)
        self.start_btn = QtWidgets.QPushButton("Start")
        self.start_btn.setFixedSize(200, 60)
        self.no_changes_footer_layout.addWidget(self.start_btn, alignment=QtCore.Qt.AlignCenter)
        self.machine_prams_layout.addWidget(self.no_changes_footer_frame)
        self.changes_footer_frame.setVisible(False)
        self.no_changes_footer_frame.setVisible(False)



        self.dialog_pages = QtWidgets.QStackedWidget()
        self.dialog_pages.addWidget(self.loading_prams_widget)
        self.dialog_pages.addWidget(self.machine_prams_widget)
        self.widget_layout.addWidget(self.dialog_pages)
        self.spinner_widget.start()
        self.start_scanning_process()

        # signals
        self.try_again_btn.clicked.connect(self.handle_try_again)
        self.close_machine_btn.clicked.connect(self.reject)
        self.close_program_btn.clicked.connect(self.reject)
        self.start_program_btn.clicked.connect(self.accept)
        self.start_btn.clicked.connect(self.accept)
        self.accept_btn.clicked.connect(self.handle_accept_changes)
        self.keep_old_btn.clicked.connect(self.accept)
        self.setMinimumSize(1000, 400)




    def _find_difference_in_prams(self, stored_machine_prams, current_prams):
        changes = {}
        for key, old_value in stored_machine_prams.items():
            new_value = self.__machine_prams.get(key)
            if new_value != old_value:
                changes[key] = [old_value, new_value]
        return len(changes) > 0, changes.copy()


    def handle_accept_changes(self):
        current_machine_prams = self.grab_prams_thread.get_machine_prams()
        stored_prams = json.load(open(CONFIGURATION_FILE_PATH))
        stored_prams.update(current_machine_prams)
        json.dump(stored_prams, open(CONFIGURATION_FILE_PATH, "w"), indent=4)
        self.accept()

    def handle_scanning_prams_finished(self):
        self.spinner_widget.stop()
        current_machine_prams = self.grab_prams_thread.get_machine_prams()
        if len(current_machine_prams) > 0:
            if os.path.isfile(CONFIGURATION_FILE_PATH):
                stored_prams = json.load(open(CONFIGURATION_FILE_PATH))
                loaded_keys = []
                change_detected = False
                for key in stored_prams:
                    loaded_keys.append(key)
                    change_detected = self.add_row(current_machine_prams.get(key), stored_prams.get(key), key) or change_detected
                for key in current_machine_prams:
                    if key not in loaded_keys:
                        change_detected = self.add_row(current_machine_prams.get(key),
                                                                          stored_prams.get(key), key) or change_detected
                if change_detected:
                    self.changes_footer_frame.setVisible(True)
                else:
                    self.no_changes_footer_frame.setVisible(True)
                    self.accept() # if no changes detected just start the machine
                self.dialog_pages.setCurrentIndex(1)

            else:
                self.loading_prams_lbl.setText("Machine Prams loaded for the first time")
                self.footer_btn_frame.setVisible(True)
                self.try_again_btn.setVisible(False)
                json.dump(current_machine_prams , open(CONFIGURATION_FILE_PATH, "w"), indent=4)

        else:
            self.loading_prams_lbl.setText(self.grab_prams_thread.get_latest_error())
            self.footer_btn_frame.setVisible(True)

    def add_row(self, current, stored, key):
        row_index = self.machine_prams_table.rowCount()
        self.machine_prams_table.insertRow(row_index)
        is_diff = False
        color = QtCore.Qt.black
        if current is None or stored is None or current!= stored:
            is_diff = True
            color = QtCore.Qt.red
        add_item_to_table(self.machine_prams_table, row_index, 0, key, color)
        add_item_to_table(self.machine_prams_table, row_index, 1, stored, color)
        add_item_to_table(self.machine_prams_table, row_index, 2, current,color)
        return is_diff

    def start_scanning_process(self):
        self.grab_prams_thread = ScanningThread()
        self.grab_prams_thread.finished.connect(self.handle_scanning_prams_finished)
        self.grab_prams_thread.start()

    def handle_try_again(self):
        self.spinner_widget.start()
        self.footer_btn_frame.setVisible(False)
        self.loading_prams_lbl.setText("Please Wait while retrieving the machine parameters.")
        self.start_scanning_process()






def __test__():
    app = QtWidgets.QApplication([])
    dialaog = RetrieveMachinePramsDialog()
    dialaog.exec_()


if __name__ == "__main__":
    __test__()
