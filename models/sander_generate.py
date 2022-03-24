"""
script to generate g-code for sanding machine
this looks at the config file and loads parameters, calculates g-code
and returns the g-code as a list.

created by: Jeremiah Lemon
3-8-2022
"""

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

"""
need to get all of the parameters from the current program

"""
MAX_WAIT_TIME = 30 # 20 sec
feed_speed_max = 15000  # we probably want to move this to a static config file
x_max_length = CustomMachineParamManager.set_value("x_max_length", 1778, auto_store=True)
y_max_width = CustomMachineParamManager.set_value("y_max_width", 660.4, auto_store=True)
sander_on_delay = .75  # we probably want to move this to a static config file
sander_off_delay = 3  # we probably want to move this to a static config file

sander_dictionary = {1: {'on': 'm62', 'off': 'm63', 'extend': 'm70', 'retract': 'm71', 'offset': 'g55'},
                     2: {'on': 'm64', 'off': 'm65', 'extend': 'm72', 'retract': 'm73', 'offset': 'g56'},
                     3: {'on': 'm66', 'off': 'm67', 'extend': 'm74', 'retract': 'm75', 'offset': 'g57'},
                     4: {'on': 'm68', 'off': 'm69', 'extend': 'm78', 'retract': 'm79', 'offset': 'g58'}
                     }


class SanderControl:
    def __init__(self, sander_db_obj: models.Sander):
        self._active_sander_id = sander_db_obj.pk
        self._sander_db_obj = sander_db_obj

    def on(self, pressure):
        if self._active_sander_id not in sander_dictionary:
            raise Exception("Sander ID is invalid")
        # put the logic

        x_sander = self._sander_db_obj.x_length

        return f'{sander_dictionary[self._active_sander_id]["extend"]}(extend)' "\n" \
               f'g4p{sander_on_delay}(delay for sander to extend)' "\n" \
               f'{sander_dictionary[self._active_sander_id]["on"]}m3s{pressure}(turn on sander and set pressure)' "\n"\
               f'g4p{sander_on_delay}(delay for sander to start)' "\n"

    def off(self):
        if self._active_sander_id not in sander_dictionary:
            raise Exception("Sander ID is invalid")

        return f'{sander_dictionary[self._active_sander_id]["retract"]}'"\n"\
                f'{sander_dictionary[self._active_sander_id]["off"]}'\
               's1000'"\n"\
               f'g4p{sander_off_delay}(delay for retraction)'"\n"\
               'm5(cancel pressure control)'"\n"


    def get_x_value(self):
        return self._sander_db_obj.x_length

    def get_y_value(self):
        return self._sander_db_obj.y_length

    def get_offset(self):
        return sander_dictionary[self._active_sander_id]['offset']

    def get_work_plane(self):
        return 'g18 g21 (workplane selection)'

    def map_pressure(self, x):
        in_min = 0
        in_max = 100
        out_min = CustomMachineParamManager.get_value("min_pressure")
        out_max = CustomMachineParamManager.get_value("max_pressure")
        shifted = int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)
        shifted2 = int((shifted - 0) * (100 - 0) / (30 - 0) + 0)
        return shifted2


class SandingGenerate:
    def __init__(self, part_type, pass_: models.SandingProgramPass, door_style: models.DoorStyle, part_length,
                 part_width):

        self.g_code = []
        self.__current_pass = pass_
        self.sander_selection = SanderControl(pass_.sander)
        self._active_sander_id = pass_.sander.pk
        self.part_length = part_length
        self.part_width = part_width
        self.frame_width = door_style.get_value("outside_edge_width") + \
                           door_style.get_value("inside_edge_width") + \
                           door_style.get_value("frame_width")
        self.hold_back = door_style.get_value("hold_back_inside_edge")
        self.pressure = 10 * (self.sander_selection.map_pressure(self.__current_pass.pressure_value))
        # print(f'pressure {self.pressure}')
        # print(f'loaded: {part_type}, {pass_.sander}, {self.part_length}, {self.part_width},'
        #      f' {self.frame_width}, {self.__current_pass.hangover_value}, {self.__current_pass.overlap_value},'
        #      f' {self.__current_pass.speed_value}, {self.hold_back}')

    def slab(self, perimeter):
        overhang_mm_x = self.__current_pass.hangover_value / 100 * self.sander_selection.get_x_value()
        # print(f'overhang x :{overhang_mm_x}')
        overhang_mm_y = self.__current_pass.hangover_value / 100 * self.sander_selection.get_y_value()
        offset_x = self.sander_selection.get_x_value() / 2 - overhang_mm_x
        offset_y = self.sander_selection.get_y_value() / 2 - overhang_mm_y
        step_over_x = float(self.part_length) / (round(
            float(self.part_length) / (self.sander_selection.get_x_value() * (1 - float(self.__current_pass.overlap_value / 100)))))
        step_over_y = float(self.part_width) / (round(
            float(self.part_width) / (self.sander_selection.get_y_value() * (1 - float(self.__current_pass.overlap_value / 100)))))
        starting_position = offset_x, offset_y
        center_line = self.part_width / 2
        print(f'center line: {center_line}')
        self.g_code.append(self.sander_selection.get_offset())
        self.g_code.append(f'f{round(feed_speed_max * int(self.__current_pass.speed_value) / 100, 1)}')
        self.g_code.append('g18 g21')
        self.g_code.append(
            f'g0x-{round(starting_position[0] + (step_over_x * 2), 1)}z{round(starting_position[1] + (step_over_y / 2), 1)}(ramp in)')
        self.g_code.append(self.sander_selection.on(self.pressure))
        self.g_code.append(
            f'g2x-{round(starting_position[0], 1)}z{round(starting_position[1], 1)}r{step_over_x * 2}(start)')
        self.g_code.append(f'g1z{round(float(self.part_width) - offset_y, 1)}(1)')
        self.g_code.append(f'g1x-{round(float(self.part_length) - offset_x, 1)}(2)')
        self.g_code.append(f'g1z{round(starting_position[1], 1)}(3)')
        if perimeter:
            self.g_code.append(
                f'g1x-{round(starting_position[0] + overhang_mm_x, 1)}z{round(starting_position[1], 1)}(start)')
            self.g_code.append(f'g1z{round(float(self.part_width) - offset_y - overhang_mm_y, 1)}(1)')
            self.g_code.append(f'g1x-{round(float(self.part_length) - offset_x - overhang_mm_x, 1)}(2)')
            self.g_code.append(f'g1z{round(starting_position[1] + overhang_mm_y, 1)}(3)')
            # print('make extra pass')
            pass  # go around outside twice
        self.g_code.append(f'g1x-{round(starting_position[0] + step_over_x, 1)}(4)')
        passes = int(int(float(self.part_width) / step_over_y) / 2)
        # print(f'passes: {passes}')
        for i in range(passes):
            self.g_code.append(f'g1z{round(float(self.part_width) - offset_y - (step_over_y * (i + 1)), 1)}(1-{i + 1})')
            self.g_code.append(
                f'g1x-{round(float(self.part_length) - (starting_position[0] + (step_over_x * (i + 1))), 1)}(2-{i + 1})')
            if (starting_position[1] + (step_over_y * (i + 1))) >= center_line:
                print('end')
                break
            self.g_code.append(f'g1z{round(starting_position[1] + (step_over_y * (i + 1)), 1)}(3-{i + 1})')
            self.g_code.append(f'g1x-{round(starting_position[0] + (step_over_x * (i + 2)), 1)}(4-{i + 1})')
            # if i == passes - 1:
            if self.part_width - offset_y - (step_over_y * (i + 1)) <= center_line:
                break
        self.g_code.append(self.sander_selection.off())
        return self.g_code

    def frame(self):
        effective_sander_width = self.sander_selection.get_y_value() - (
                (self.sander_selection.get_y_value() * (self.__current_pass.hangover_value / 100)) * 2)
        if self.frame_width <= effective_sander_width:
            center_positions = (self.frame_width / 2, self.frame_width / 2), \
                               (self.frame_width / 2, self.part_width - (self.frame_width / 2)), \
                               (self.part_length - (self.frame_width / 2), self.part_width - (self.frame_width / 2)), \
                               (self.part_length - (self.frame_width / 2), self.frame_width / 2)
            print(f'center: {center_positions}')
            self.g_code.append(self.sander_selection.get_offset())
            self.g_code.append(f'f{round(feed_speed_max * int(self.__current_pass.speed_value) / 100, 1)}')
            self.g_code.append(self.sander_selection.get_work_plane())
            self.g_code.append(f'g0x-{center_positions[0][0]}z{center_positions[0][0]}')
            self.g_code.append(self.sander_selection.on(self.pressure))
            self.g_code.append(f'g1z{center_positions[1][1]}')
            self.g_code.append(f'g1x-{center_positions[2][0]}')
            self.g_code.append(f'g1z{center_positions[3][1]}')
            self.g_code.append(f'g1x-{center_positions[0][0]}')
            self.g_code.append(self.sander_selection.off())
            # self.g_code.append('g53g0x0z0')
        else:
            start_positions = (0, 0), (0, self.part_width), (self.part_length, self.part_width), (self.part_length, 0)
            inside_edge = (self.frame_width, self.frame_width), \
                          (self.frame_width, self.part_width - self.frame_width), \
                          (self.part_length - self.frame_width, self.part_width - self.frame_width), \
                          (self.part_length - self.frame_width, self.frame_width)
            overhang_mm_x = self.__current_pass.hangover_value / 100 * self.sander_selection.get_x_value()
            # print(f'overhang x :{overhang_mm_x}')
            overhang_mm_y = self.__current_pass.hangover_value / 100 * self.sander_selection.get_y_value()
            offset_x = self.sander_selection.get_x_value() / 2 - overhang_mm_x
            offset_y = self.sander_selection.get_y_value() / 2 - overhang_mm_y
            print('sand in two passes')
            print(f'starting: {start_positions}')
            print(f'inside: {inside_edge}')
            print(f'offsets: {offset_x}, {offset_y}')
            self.g_code.append(self.sander_selection.get_offset())
            self.g_code.append(f'f{round(feed_speed_max * int(self.__current_pass.speed_value) / 100, 1)}')
            self.g_code.append(self.sander_selection.get_work_plane())
            self.g_code.append(f'g0x-{start_positions[0][0] + offset_x}z{start_positions[0][1] + offset_y}')
            self.g_code.append(self.sander_selection.on(self.pressure))
            self.g_code.append(f'g1z{start_positions[1][1] - offset_y}')
            self.g_code.append(f'g1x-{start_positions[2][0] - offset_x}')
            self.g_code.append(f'g1z{start_positions[3][1] + offset_y}')
            self.g_code.append(f'g1x-{start_positions[0][0] + offset_x}')
            self.g_code.append(f'g1x-{inside_edge[0][0] - offset_x}z{inside_edge[0][1] - offset_y}')
            self.g_code.append(f'g1z{inside_edge[1][1] + offset_y}')
            self.g_code.append(f'g1x-{inside_edge[2][0] + offset_x}')
            self.g_code.append(f'g1z{inside_edge[3][1] - offset_y}')
            self.g_code.append(f'g1x-{inside_edge[0][0] - offset_x}')
            self.g_code.append(self.sander_selection.off())

        return self.g_code

    def panel(self, perimeter, entire_panel):
        stile = self.frame_width
        width = float(self.part_width)
        length = float(self.part_length)
        overlap = float(self.__current_pass.overlap_value)
        hold_back = float(self.hold_back)
        panel_size = length - (stile * 2), width - (stile * 2)
        panel_corners = (stile, stile), (stile, width - stile), (length - stile, width - stile), (length - stile, stile)
        print(f'panel corners: {panel_corners}')
        step_over = length / (round(length / (self.sander_selection.get_x_value() * (1 - overlap / 100)))), \
                    width / (round(width / (self.sander_selection.get_y_value() * (1 - overlap / 100))))
        print(f'step over x : {step_over[0]} y: {step_over[1]}')
        offset_x = float(self.sander_selection.get_x_value() / 2) + hold_back
        offset_y = float(self.sander_selection.get_y_value() / 2) + hold_back
        print(f'panel size{panel_size}, offset: {offset_x, offset_y}')
        if self.sander_selection.get_y_value() >= panel_size[1]:
            print('sander too wide')
        elif self.sander_selection.get_x_value() >= panel_size[0]:
            print('sander too long')
        print('you selected panel')
        panel_start = self.frame_width + (float(self.sander_selection.get_x_value()) / 2) + \
                      hold_back, self.frame_width + \
                      (float(self.sander_selection.get_y_value()) / 2) + hold_back
        passes = int(
            ((panel_size[1] - hold_back) / step_over[1]) / 2) - 1
        print(f'panel start {panel_start}, passes: {passes}')
        self.g_code.append(self.sander_selection.get_offset() + " (set wco for sander)")
        self.g_code.append(
            f'f{round(feed_speed_max * int(self.__current_pass.speed_value) / 100, 1)}(set feed speed)')
        self.g_code.append('g18 g21(work-plane xz and mm)')
        self.g_code.append(f'g0x-{panel_start[0] + hold_back}z{panel_start[1] + hold_back}(ramp in)')
        self.g_code.append(self.sander_selection.on(self.pressure))
        self.g_code.append(f'g3x-{panel_start[0]}z{panel_start[1]}r{hold_back}(starting)')
        self.g_code.append(f'g1x-{round(panel_corners[3][0] - offset_x, 1)}(2)')
        self.g_code.append(f'g1z{round(panel_corners[2][1] - offset_y, 1)}(3)')
        self.g_code.append(f'g1x-{round(panel_start[0], 1)}(4)')
        if entire_panel:
            if perimeter:
                self.g_code.append(f'g1z{panel_start[1]}(1)')
                self.g_code.append(f'g1x-{round(panel_corners[3][0] - offset_x, 1)}(2)')
                self.g_code.append(f'g1z{round(panel_corners[2][1] - offset_y, 1)}(3)')
                self.g_code.append(f'g1x-{round(panel_start[0], 1)}(4)')
            if passes == 0:
                self.g_code.append(f'g1z{((((panel_corners[2][1] - offset_y) - panel_start[1]) / 2) + panel_start[1])}')
                self.g_code.append(f'g1x-{round(float(length) - (panel_start[0] + step_over[0]), 1)}')
            for i in range(passes):
                self.g_code.append(
                    f'g1z{round(panel_corners[3][1] + offset_y + (step_over[1] * (i + 1)), 1)}(1-{i + 1})')
                self.g_code.append(
                    f'g1x-{round(float(length) - (panel_start[0] + (step_over[0] * (i + 1))), 1)}(2-{i + 1})')
                if i == passes - 1 and (passes % 2) == 0:  # break here if the number of passes was even
                    break
                self.g_code.append(
                    f'g1z{round(panel_corners[2][1] - ((step_over[1]) * (i + 1) + offset_y), 1)}(3-{i + 1})')
                self.g_code.append(f'g1x-{round(panel_start[0] + (step_over[0] * (i + 2)), 1)}(4-{i + 1})')
                if i == passes - 1:
                    break
                # todo break here if the number of passes was odd
        else:
            if perimeter:
                self.g_code.append(f'g1z{panel_start[1]}')
                self.g_code.append(f'g1x-{round(panel_corners[3][0] - offset_x, 1)}(2)')
                self.g_code.append(f'g1z{round(panel_corners[2][1] - offset_y, 1)}(3)')
                self.g_code.append(f'g1x-{round(panel_start[0], 1)}(4)')
            self.g_code.append(f'g1z{panel_start[1]}')
            self.g_code.append(f'g3x-{panel_start[0] + hold_back}z{panel_start[1] + hold_back}r{hold_back}(ramp out)')

        self.g_code.append(self.sander_selection.off())

        return self.g_code

    def end_cycle(self):
        buffer = []
        buffer.append('m5(deactivate vacuum)')
        buffer.append('g54(reset wco)')
        buffer.append(f'g0x-900z0(go to park position)')
        return buffer


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
        self.starting_rough = CustomMachineParamManager.get_value('probe_x_zero'),\
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

    def send_and_get_response(self, cmd , delay_ms: int = 500, decode_block_flag=False):
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
                    if result is not None or alarm_no >0:
                        break
        return result, alarm_no

    def calibrate(self):

        self.send_and_get_response('g21g54(set units and wco)')
        self.send_and_get_response(f'g0x-{self.starting_rough[0] + self.offset_in}z-{self.starting_rough[1] - self.offset_in}')
        #self.g_code.append('g38.5x0f1200')
        test_probe = self.send_and_get_response('?')
        decoded_response, alarm_no = self.send_and_get_response('g38.5x0f1200', decode_block_flag=True)
        if decoded_response is None:
            self.calibrationFailedSignal.emit()
        result_x_minus = decoded_response[0]  # todo this will be replaced with result from probe
        self.send_and_get_response(f'g0x-{self.starting_rough[0] + self.offset_in}z-{self.starting_rough[1] - self.offset_in}')
        decoded_response, alarm_no = self.send_and_get_response(f'g38.5z-{self.starting_rough[1] + 10}', decode_block_flag=True)
        if decoded_response is None:
            self.calibrationFailedSignal.emit()
        result_z_plus = decoded_response[2]  # todo get return of probe
        self.send_and_get_response(f'g0x-{self.starting_rough[0] + self.cal_size[0] - self.offset_in}z-{self.starting_rough[1] - self.offset_in}')
        decoded_response, alarm_no=self.send_and_get_response(f'g38.5x-1700', decode_block_flag=True)
        if decoded_response is None:
            self.calibrationFailedSignal.emit()
        result_x_plus = decoded_response[0]  # todo get return of probe
        self.send_and_get_response(f'g0x-{self.starting_rough[0] + self.offset_in}z-{self.starting_rough[1] - self.cal_size[1] + self.offset_in}')
        decoded_response, alarm_no= self.send_and_get_response('g38.5z0', decode_block_flag=True)
        if decoded_response is None:
            self.calibrationFailedSignal.emit()
        self.send_and_get_response('g0x-900z0(park machine)')
        result_z_minus = decoded_response[2]  # todo get return of probe
        print(f'results: {result_x_minus}, {result_x_plus}. {result_z_plus}, {result_z_minus}')
        result_size = -1 * (result_x_plus - result_x_minus), result_z_minus - result_z_plus
        CustomMachineParamManager.set_value("probe_x_diameter", (self.cal_size[0] - result_size[0]), auto_store=True)
        CustomMachineParamManager.set_value("probe_y_diameter", (self.cal_size[1] - result_size[1]), auto_store=True)
        CustomMachineParamManager.set_value('probe_x_zero', (-1 * result_x_minus) - CustomMachineParamManager.get_value('probe_x_diameter'), auto_store=True)
        CustomMachineParamManager.set_value('probe_y_zero', (-1 * result_z_plus) + CustomMachineParamManager.get_value('probe_y_diameter'), auto_store=True)

    def probe_part(self):
        step_back = 30
        x_y_0 = CustomMachineParamManager.get_value('probe_x_zero'), CustomMachineParamManager.get_value('probe_y_zero')
        self.send_and_get_response('g21g54(set units and wco)')
        self.send_and_get_response('g0x-900z0')
        decoded_response, alarm_no = self.send_and_get_response(f'g38.2x-{x_y_0[0] + (step_back*4)}z-{x_y_0[1] - step_back}f8000', decode_block_flag=True)
        if alarm_no == 5:
            # @todo for some reason i am not getting into this if statement when i should be, i suspect it is because it is reading the response to the unlock
            print('part not found yet')
            decoded_response, alarm_no = self.send_and_get_response(f'g38.2x-{x_y_0[0] + step_back}', decode_block_flag=True)
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
        self.send_and_get_response(f'g0z-{(-1*result_z)  + step_back}')
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


def turn_vacuum_on(sensors_board_ref, ch):
    if sensors_board_ref is not None:
        sensors_board_ref.turn_vacuum_on(ch)
    else:
        pass
        # print(f"debug mode turn on vacuum {ch}")


def turn_vacuum_off(sensors_board_ref, ch):
    if sensors_board_ref is not None:
        sensors_board_ref.turn_vacuum_off(ch)
    else:
        # print(f"debug mode turn off vacuum {ch}")
        pass


def probe_test():
    all_g_codes = []
    generate_probe = Probe()
    all_g_codes.extend(generate_probe.calibrate())
    print(all_g_codes, sep="\n")
    print(generate_probe.probe_part())


def generate(sensors_board_ref=None):
    door_style = db_utils.get_current_door_style()
    passes = db_utils.get_current_program()  # this object contain multiple paths
    # todo need to add switch for right side
    # print(f'part type: {part_type}')
    zone = CustomMachineParamManager.get_value('side')
    probing_on = CustomMachineParamManager.get_value('probing_on')

    # sensors_board_ref.turn_vacuum_on()
    # sensors_board_ref.send_vacuum_value(mode, param)
    if zone == 'left':
        part_length = CustomMachineParamManager.get_value("left_part_length")
        part_width = CustomMachineParamManager.get_value("left_part_width")
        part_type = CustomMachineParamManager.get_value('left_slab_selected')
        if part_length >= 1488:
            turn_vacuum_on(sensors_board_ref, 6)
        elif part_length >= 950:
            turn_vacuum_on(sensors_board_ref, 5)
        elif part_length >= 700:
            turn_vacuum_on(sensors_board_ref, 4)
        elif part_length >= 300:
            turn_vacuum_on(sensors_board_ref, 3)
        else:
            print('part is too short for work holding on x')

        if part_width >= 360:
            turn_vacuum_on(sensors_board_ref, 1)
        elif part_width >= 135:
            turn_vacuum_on(sensors_board_ref, 2)
            print('turning on vacuum 2')
        else:
            print('part is too short for work holding on x')
    if zone == 'right':
        part_length = CustomMachineParamManager.get_value("right_part_length")
        part_width = CustomMachineParamManager.get_value("right_part_width")
        part_type = CustomMachineParamManager.get_value('right_slab_selected')
        probing_on = CustomMachineParamManager.get_value('')
        print(f'length: {part_length} width: {part_width} type: {part_type}')
        if part_length >= 700:
            turn_vacuum_on(sensors_board_ref, 5)
        elif part_length >= 300:
            turn_vacuum_on(sensors_board_ref, 6)
        else:
            print('part is too short for work holding on x')

        if part_width >= 360:
            turn_vacuum_on(sensors_board_ref, 8)
        elif part_width >= 135:
            turn_vacuum_on(sensors_board_ref, 7)
        else:
            print('part is too short for work holding on x')
        # todo need a strategy to apply a compensation for right,
        # 1: change x0 to left end of piece, then send the same program we send for left zone
        # 2: change x0 to right corner of machine, invert x axis
    if sensors_board_ref is not None:
        sensors_board_ref.send_vacuum_value(1, 30)  # activating pressure at full pressure. not sure if this is needed.

    # all_g_codes = []
    for index, pass_ in enumerate(passes):
        print(f"pass no {index}")
        generate_code = SandingGenerate(part_type, pass_, door_style, part_length, part_width)
        if part_type:  # if the part is a 5-piece
            if pass_.contain_frames:
                generate_code.frame()
            if pass_.contain_panels:
                generate_code.panel(pass_.make_extra_pass_around_perimeter, pass_.is_entire_panel)
        else:  # the part is a slab
            if pass_.contain_slabs:
                generate_code.slab(pass_.make_extra_pass_around_perimeter)
        all_g_codes.extend(generate_code.g_code)
        # all_g_codes.append("(the end of pass 1)")
    # todo add logic to turn off vacuum and park machine.
    

    """x_offset = max_length - part_length
    for each x-:
        old x - x_offset"""


    if zone == 'right':  # need to offset x dims by maximum length, and invert all x  todo
        for index, x in enumerate(all_g_codes):
        x_offset =  CustomMachineParamManager.get_value('x_max_length') - part_length
        print(f'offset: {x_offset}')
        for index, x in enumerate(generate_code.g_code):
            if x[0] == "g" and x[2] == "x":
                if x[3] == "-":
                    all_g_codes[index] = x.replace("x-", "x")
                    s = ""
                    for i in range(4, len(x)):
                      if x[i] in "0123456789.":
                          s += x[i]
                      else:
                          break
                    new_value = round(-1*float(s) - x_offset , 2)
                    new_string = x[:3] + str(new_value)+x[i:]
                    generate_code.g_code[index] = new_string
                else:
                    all_g_codes[index] = x.replace("x", "x-")
                #  rint(f"old: {x} new {all_g_codes[index]}")

    all_g_codes.extend(generate_code.end_cycle())
    return all_g_codes
    # print(*all_g_codes, sep="\n")



if __name__ == "__main__":
    probe_test()
    #  generate()
