import os
import time

#  from tkinter.messagebox import NO

try:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    from django.core.wsgi import get_wsgi_application

    application = get_wsgi_application()
except Exception as e:
    print(e)

from configurations.custom_pram_loader import CustomMachineParamManager
from models import db_utils
from apps.sanding_machine import models
from statistics import mean
from PySide2 import QtCore


class Probe(QtCore.QThread):
    calibrationFailedSignal = QtCore.Signal()
    partProbbeingFinishedSignal = QtCore.Signal(str, float, float)

    def __init__(self, serial_interface, in_calibration_mode=False, side="left"):
        super(Probe, self).__init__()
        self.g_code = []
        self.in_calibration_mode = in_calibration_mode
        self.current_side = side
        self.serial_interface = serial_interface
        self.cal_size = CustomMachineParamManager.get_value("probe_cal_x", None), CustomMachineParamManager.get_value(
            "probe_cal_y", None)  # this will come from settings page
        if self.cal_size[0] is None or self.cal_size[1] is None:
            raise ValueError("you have to set the probe values from the setting page first.")
        self.starting_rough = CustomMachineParamManager.get_value('probe_x_zero'), \
                              CustomMachineParamManager.get_value('probe_y_zero')
        self.offset_in = 75

    def run(self):
        self.serial_interface.grbl_stream.reset_prob_buffer()
        if self.in_calibration_mode:
            self.calibrate()
        else:
            self.probe_part()

    def decode_response(self, response_list):
        values = None
        alarm_no = 0
        for rec_bytes in response_list:
            rec_str = rec_bytes.decode()
            rec_str = rec_str.rstrip("\r\n")
            # [b'[PRB:-137.018,0.000,-623.444:1]\r\n', b'ok\r\n', b'ok\r\n']
            if "PRB:" in rec_str:
                sub_str = rec_str[5:-3].split(",")
                values = [float(val) for val in sub_str]
            elif "PN:P" in rec_str:
                print('probe is on')
                break
            elif "ALARM:4" in rec_str:
                self.serial_interface.grbl_stream.send_command_directly(b'$x')
                alarm_no = 4
                time.sleep(2)
            elif "ALARM:5" in rec_str:
                self.serial_interface.grbl_stream.send_command_directly(b'$x')
                alarm_no = 5
                time.sleep(2)
        return values, alarm_no

    def send_and_get_response(self, cmd, delay_ms: int = 500, decode_block_flag=False):
        result = None
        alarm_no = 0
        cmd_str = cmd + "\r\n"
        self.serial_interface.grbl_stream.send_command_directly(cmd_str.encode(), delay_ms, decode_block_flag)
        if decode_block_flag is True:
            start_time = time.time()
            while time.time() - start_time < MAX_WAIT_TIME:
                rec_bytes_list = self.serial_interface.grbl_stream.receive_bytes(timeout=0.1)
                if rec_bytes_list is None:
                    self.msleep(50)
                else:
                    result, alarm_no = self.decode_response(rec_bytes_list)
                    if result is not None or alarm_no > 0:
                        break
        return result, alarm_no

    def calibrate(self):

        self.send_and_get_response('g21g54(set units and wco)')
        self.send_and_get_response(
            f'g0x-{self.starting_rough[0] + self.offset_in}z-{self.starting_rough[1] - self.offset_in}')
        # self.g_code.append('g38.5x0f1200')
        test_probe = self.send_and_get_response('?')
        decoded_response, alarm_no = self.send_and_get_response('g38.5x0f1200', decode_block_flag=True)
        if decoded_response is None:
            self.calibrationFailedSignal.emit()
        result_x_minus = decoded_response[0]  # todo this will be replaced with result from probe
        self.send_and_get_response(
            f'g0x-{self.starting_rough[0] + self.offset_in}z-{self.starting_rough[1] - self.offset_in}')
        decoded_response, alarm_no = self.send_and_get_response(f'g38.5z-{self.starting_rough[1] + 10}',
                                                                decode_block_flag=True)
        if decoded_response is None:
            self.calibrationFailedSignal.emit()
        result_z_plus = decoded_response[2]  # todo get return of probe
        self.send_and_get_response(
            f'g0x-{self.starting_rough[0] + self.cal_size[0] - self.offset_in}z-{self.starting_rough[1] - self.offset_in}')
        decoded_response, alarm_no = self.send_and_get_response(f'g38.5x-1700', decode_block_flag=True)
        if decoded_response is None:
            self.calibrationFailedSignal.emit()
        result_x_plus = decoded_response[0]  # todo get return of probe
        self.send_and_get_response(
            f'g0x-{self.starting_rough[0] + self.offset_in}z-{self.starting_rough[1] - self.cal_size[1] + self.offset_in}')
        decoded_response, alarm_no = self.send_and_get_response('g38.5z0', decode_block_flag=True)
        if decoded_response is None:
            self.calibrationFailedSignal.emit()
        self.send_and_get_response('g0x-900z0(park machine)')
        result_z_minus = decoded_response[2]  # todo get return of probe
        print(f'results: {result_x_minus}, {result_x_plus}. {result_z_plus}, {result_z_minus}')
        result_size = -1 * (result_x_plus - result_x_minus), result_z_minus - result_z_plus
        CustomMachineParamManager.set_value("probe_x_diameter", (self.cal_size[0] - result_size[0]), auto_store=True)
        CustomMachineParamManager.set_value("probe_y_diameter", (self.cal_size[1] - result_size[1]), auto_store=True)
        CustomMachineParamManager.set_value('probe_x_zero', (-1 * result_x_minus) - CustomMachineParamManager.get_value(
            'probe_x_diameter'), auto_store=True)
        CustomMachineParamManager.set_value('probe_y_zero', (-1 * result_z_plus) + CustomMachineParamManager.get_value(
            'probe_y_diameter'), auto_store=True)

    def probe_part(self):
        if self.current_side == "right":
            print('probing on right side not implemented')
            return  # todo finish logic for left or right probe.
        step_back = 30
        x_y_0 = CustomMachineParamManager.get_value('probe_x_zero'), CustomMachineParamManager.get_value('probe_y_zero')
        self.send_and_get_response('g21g54(set units and wco)')
        self.send_and_get_response('g0x-900z0')
        decoded_response, alarm_no = self.send_and_get_response(
            f'g38.2x-{x_y_0[0] + (step_back * 4)}z-{x_y_0[1] - step_back}f8000', decode_block_flag=True)
        if alarm_no == 5:
            # @todo for some reason i am not getting into this if statement when i should be, i suspect it is because it is reading the response to the unlock
            print('part not found yet')
            decoded_response, alarm_no = self.send_and_get_response(f'g38.2x-{x_y_0[0] + step_back}',
                                                                    decode_block_flag=True)
            if alarm_no == 5:
                print('no part found, canceling probe')
                self.send_and_get_response('g0x-900z0')
                return
        elif alarm_no == 4:
            print('probing failed')
            self.send_and_get_response('g0x-900z0')
            # cancel the probing routine
            return
        if decoded_response is None:
            self.calibrationFailedSignal.emit()
            return
        result_1 = decoded_response[2]
        self.send_and_get_response(f'g0x-{-1 * (decoded_response[0]) - step_back}z-{(-1 * result_1) + step_back}')
        decoded_response, alarm_no = self.send_and_get_response(f'g38.4z0f2400', decode_block_flag=True)
        if alarm_no == 5:
            print('part may be too big')
            return
        elif alarm_no == 4:
            print('probe not in correct state')
        if decoded_response is None:
            self.calibrationFailedSignal.emit()
            return
        result_z = decoded_response[2]
        self.send_and_get_response(f'g0z-{(-1 * result_z) + step_back}')
        decoded_response = self.send_and_get_response('g38.5x-1700f2400', decode_block_flag=True)
        if decoded_response is None:
            self.calibrationFailedSignal.emit()
            return
        result_x = decoded_response[0][0]
        print(f'result {result_x}, {result_z}')
        part_size = (-1 * result_x) - x_y_0[0], x_y_0[1] - (-1 * result_z)
        CustomMachineParamManager.set_value(f"prob_{self.current_side}_size", part_size, auto_store=True)
        self.partProbbeingFinishedSignal.emit(self.current_side, part_size[0], part_size[1])
        print(f'part size: {part_size}')

