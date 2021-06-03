import logging
import time
from enum import Enum

import serial
from PySide2 import QtCore

import configurations.static_app_configurations as static_configurations

module_logger = logging.getLogger(static_configurations.LOGGER_NAME)


class RecState(Enum):
    waitStartHi = 0
    waitStartLow = 1
    recData = 2
    waitCrc = 3


class RecPacketType(Enum):
    EstopStatusPacket = 0


class ModuleStatus(Enum):
    STATUS_UNKNOWN = 0
    STATUS_DISABLED = 1
    STATUS_ENABLED = 2
    STATUS_ERROR = 3


class SignalToModule(Enum):
    MODULE_NOP = 0
    MODULE_UPDATE_STATUS = 1
    MODULE_TURN_OFF = 2
    MODULE_TURN_ON = 3


START_HI = 0xAA
START_LO = (0xAA ^ 255)
DATA_LEN = 3  # packet type, 2 bytes payload


class EStopSerialInterface(QtCore.QThread):
    updateEstopSignal = QtCore.Signal(str)

    def __init__(self):
        super(EStopSerialInterface, self).__init__()
        self.__is_serial_dev_connected = False
        self.__serial_dev = None
        self.data_buffer = []
        self.__current_rec_state = RecState.waitStartHi
        self.__last_time_status_checked = time.time()

    def run(self):
        if static_configurations.IS_ESTOP_MODULE_ENABLED is False:
            module_logger.info("the sensors are disabled by the configurations")
            return
        while not self.isInterruptionRequested():
            if not self.__is_serial_dev_connected:
                self.reconnect()
                if not self.__is_serial_dev_connected:
                    self.sleep(4)
                    continue
            try:
                while self.__serial_dev.inWaiting() > 0:
                    all_incoming_bytes = self.__serial_dev.read(self.__serial_dev.inWaiting())
                    for byte in all_incoming_bytes:
                        if self.__current_rec_state == RecState.waitStartHi:
                            if byte == START_HI:
                                self.__current_rec_state = RecState.waitStartLow
                        elif self.__current_rec_state == RecState.waitStartLow:
                            if byte == START_LO:
                                self.data_buffer.clear()
                                self.__current_rec_state = RecState.recData
                        elif self.__current_rec_state == RecState.recData:
                            self.data_buffer.append(byte)
                            if len(self.data_buffer) >= DATA_LEN:
                                self.__current_rec_state = RecState.waitCrc
                        elif self.__current_rec_state == RecState.waitCrc:
                            calculated_crc = self.calculate_crc8(self.data_buffer)
                            if calculated_crc == byte:
                                packet_type = self.data_buffer[0]
                                packet_value = (self.data_buffer[1] << 8) + self.data_buffer[2]
                                packet_type = RecPacketType(packet_type)
                                if packet_type == RecPacketType.EstopStatusPacket:
                                    self.__last_time_status_checked = time.time()
                                    if packet_value == ModuleStatus.STATUS_UNKNOWN:
                                        self.updateEstopSignal.emit("unknown status")
                                    elif packet_value == ModuleStatus.STATUS_DISABLED:
                                        self.updateEstopSignal.emit("E-stop disabled")
                                    elif packet_value == ModuleStatus.STATUS_ENABLED:
                                        self.updateEstopSignal.emit("E-stop enabled")
                                    elif packet_value == ModuleStatus.STATUS_ERROR:
                                        self.updateEstopSignal.emit("E-stop error")
                            self.__current_rec_state = RecState.waitStartHi
                else:
                    self.msleep(50)  # sleep 50 ms
                current_time = time.time()
                if (
                        current_time - self.__last_time_status_checked) >= static_configurations.ESTOP_CHECK_STATUS_EVERY:
                    self.get_module_status()
                    self.__last_time_status_checked = time.time()
            except OSError:
                self.__is_serial_dev_connected = False
                # save close the port
        if self.__serial_dev:
            try:
                self.__serial_dev.close()
            except:
                pass
        module_logger.info("service close after the thread finished")

    def turn_on_module(self):
        self.send_signal(SignalToModule.MODULE_TURN_ON)

    def turn_off_module(self):
        self.send_signal(SignalToModule.MODULE_TURN_ON)

    def get_module_status(self):
        self.send_signal(SignalToModule.MODULE_UPDATE_STATUS)

    def send_signal(self, signal_type: SignalToModule):
        packet = [START_HI, signal_type.value, signal_type.value ^ 255]
        packet_bytes = bytes(packet)
        self.__serial_dev.write(packet_bytes)

    @staticmethod
    def calculate_crc8(data):
        crc = 0
        for i in range(len(data)):
            byte = data[i]
            for b in range(8):
                fb_bit = (crc ^ byte) & 0x01
                if fb_bit == 0x01:
                    crc = crc ^ 0x18
                crc = (crc >> 1) & 0x7f
                if fb_bit == 0x01:
                    crc = crc | 0x80
                byte = byte >> 1
        return crc

    def reconnect(self):
        self.__is_serial_dev_connected = False
        if self.__serial_dev:
            try:
                self.__serial_dev.close()
            except:
                pass
            self.__serial_dev = None
        try:
            self.__serial_dev = serial.Serial(static_configurations.ESTOP_MODULE_COM_PORT,
                                              static_configurations.ESTOP_MODULE_BAUD_RATE,
                                              timeout=0.5)
            if self.__serial_dev.isOpen():
                self.__is_serial_dev_connected = True
                self.__serial_dev.flush()
        except serial.SerialException as e:
            module_logger.exception(e)
