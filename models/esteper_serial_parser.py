import serial
from PySide2 import QtCore
from enum import Enum
class RecState(Enum):
    waitStartHi = 0
    waitStartLow = 1
    recData = 2
    waitCrc = 3

class RecPacketType(Enum):
    EstepperStatusPacket = 0

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
START_LO = (0xAA^255)
DATA_LEN = 3 # packet type, 2 bytes payload

class EStepperSerialInterface(QtCore.QThread):
    updateEstepperSignal = QtCore.Signal(str)
    def __init__(self):
        super(EStepperSerialInterface, self).__init__()
        self.__serial_interface = serial.Serial("/dev/ttyACM0", 4800)
        self.data_buffer = []
        self.__current_rec_state = RecState.waitStartHi

    def run(self):
        while not self.isInterruptionRequested():
            self.msleep(0.02)
            while  self.__serial_interface.inWaiting() > 0:
                all_incoming_bytes = self.__serial_interface.read(self.__serial_interface.inWaiting())
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
                            packet_value = (self.data_buffer[1]<<8) + self.data_buffer[2]
                            if packet_type == RecPacketType.EstepperStatusPacket:
                                if packet_value == ModuleStatus.STATUS_UNKNOWN:
                                    self.updateEstepperSignal.emit("unknown status")
                                elif packet_value == ModuleStatus.STATUS_DISABLED:
                                    self.updateEstepperSignal.emit("estepper disabled")
                                elif packet_value == ModuleStatus.STATUS_ENABLED:
                                    self.updateEstepperSignal.emit("estepper enabled")
                                elif packet_value == ModuleStatus.STATUS_ERROR:
                                    self.updateEstepperSignal.emit("estepper error")
                        self.__current_rec_state = RecState.waitStartHi

    def send_signal(self, signal_type:SignalToModule):
        packet = [START_HI, START_LO, signal_type, signal_type^255]
        packet_bytes = bytes(packet)
        self.__serial_interface.write(packet_bytes)


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
