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

    def __init__(self):
        super(SensorsSerialConnector, self).__init__()
        self.__is_serial_dev_connected = False
        self.__serial_dev = None

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
                    if len(rec_bytes) == 7:
                        header = str(rec_bytes[0:3], "utf-8")
                        if header == "val":
                            rec_bytes = rec_bytes[3:-2]
                            val = int.from_bytes(rec_bytes, "big")
                            bits = []
                            for i in range(16):
                                bit_val = val & 1
                                val = val >> 1
                                bits.append(bit_val)
                            self.newReading.emit(bits)
                    elif len(rec_bytes) > 6:
                        header = str(rec_bytes[0:6], "utf-8")
                        if header == "weight":
                            try:
                                val = float(rec_bytes[6:-2])
                                self.weightChanged.emit(val)
                            except:
                                pass

                except OSError:
                    self.__is_serial_dev_connected = False
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
