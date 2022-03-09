import logging
import os
import time

import serial
from PySide2 import QtCore

from configurations import common_configurations

LOG_FILE_PATH = os.path.join(common_configurations.LOGGER_BASE, common_configurations.SENSOR_LOGGER_FILE)
sensors_serial_logger = logging.getLogger(common_configurations.LOGGER_NAME)
sensors_serial_logger.setLevel(common_configurations.SENSOR_LOGGING_LVL)
fh = logging.FileHandler(LOG_FILE_PATH)
fh.setLevel(common_configurations.SENSOR_LOGGING_LVL)
formatter = logging.Formatter(common_configurations.SENSOR_LOGGING_FORMAT)
fh.setFormatter(formatter)
sensors_serial_logger.addHandler(fh)


class SensorsSerialConnector(QtCore.QThread):
    newReading = QtCore.Signal(list)
    weightChanged = QtCore.Signal(float)
    start_left_signal = QtCore.Signal()
    start_right_signal = QtCore.Signal()

    def __init__(self):
        super(SensorsSerialConnector, self).__init__()
        self.__is_serial_dev_connected = False
        self.__serial_dev = None
        self.is_left_pressed = False
        self.is_right_pressed = False

    def send_message(self, msg_to_send):
        if self.__is_serial_dev_connected:
            try:
                self.__serial_dev.write(msg_to_send)
                sensors_serial_logger.debug(">> {}".format(str(msg_to_send, "utf-8")))
            except OSError:
                self.__is_serial_dev_connected = False

    def run(self):
        if not common_configurations.IS_SENSOR_MODULE_ENABLED:
            sensors_serial_logger.info("the sensors are disabled by the configurations")
            return
        while not self.isInterruptionRequested():
            if not self.__is_serial_dev_connected:
                self.reconnect()
                if not self.__is_serial_dev_connected:
                    self.sleep(4)
                    continue
            while self.__serial_dev.inWaiting() > 0:
                try:
                    rec_bytes = self.__serial_dev.read_until()
                    rec_str = str(rec_bytes, "utf-8").rstrip("\r\n")
                except OSError:
                    self.__is_serial_dev_connected = False
                else:
                    # $0,0*
                    if rec_str.startswith("$") and rec_str.endswith("*"):
                        control_signals = [int(val) for val in rec_str[1:-1].split(",")]
                        if len(control_signals) == 2:
                            if control_signals[0] == 1 and not self.is_left_pressed:
                                self.start_left_signal.emit()
                                self.is_left_pressed = True
                            else:
                                self.is_left_pressed = False
                            if control_signals[1] == 1 and not self.is_right_pressed:
                                self.start_right_signal.emit()
                                self.is_right_pressed = True
                            else:
                                self.is_right_pressed = False
                    else:
                        print(f"failed to decode {rec_str}")
            else:
                time.sleep(0.05)
        # save close the port
        if self.__serial_dev:
            try:
                self.__serial_dev.close()
            except:
                pass
        sensors_serial_logger.info("service close after the thread finished")



    def turn_on_servo(self):
        self.send_message(b"OO")

    def turn_off_servo(self):
        self.send_message(b"FF")

    def reconnect(self):
        self.__is_serial_dev_connected = False
        if self.__serial_dev:
            try:
                self.__serial_dev.close()
            except:
                pass
            self.__serial_dev = None
        try:
            self.__serial_dev = serial.Serial(common_configurations.SENSOR_MODULE_COM_PORT,
                                              common_configurations.SENSOR_MODULE_BAUD_RATE,
                                              timeout=0.5)
            if self.__serial_dev.isOpen():
                self.__is_serial_dev_connected = True
                self.__serial_dev.flush()
        except serial.SerialException as e:
            print(e)
