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
from math import ceil as ceil

"""
need to get all of the parameters from the current program

"""
MAX_WAIT_TIME = 30  # 20 sec
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
               f'{sander_dictionary[self._active_sander_id]["on"]}m3s{pressure}(turn on sander and set pressure)' "\n" \
               f'g4p{sander_on_delay}(delay for sander to start)' "\n"

    def off(self):
        if self._active_sander_id not in sander_dictionary:
            raise Exception("Sander ID is invalid")

        return f'{sander_dictionary[self._active_sander_id]["retract"]}'"\n" \
               f'{sander_dictionary[self._active_sander_id]["off"]}' \
               's1000'"\n" \
               f'g4p{sander_off_delay}(delay for retraction)'"\n" \
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
    def __init__(self, pass_: models.SandingProgramPass, door_style: models.DoorStyle, part_length,
                 part_width):

        self.g_code = []
        self.__current_pass = pass_
        self.sander_selection = SanderControl(pass_.sander)
        self._active_sander_id = pass_.sander.pk
        self.part_length = part_length
        self.part_width = part_width
        # self.frame_width = door_style.get_value("outside_edge_width") + \
        #                    door_style.get_value("inside_edge_width") + \
        #                    door_style.get_value("frame_width")
        # self.hold_back = door_style.get_value("hold_back_inside_edge")
        self.frame_add = door_style.get_value("inside_edge_width") + door_style.get_value("hold_back_inside_edge")
        self.pressure = 10 * (self.sander_selection.map_pressure(self.__current_pass.pressure_value))
        # print(f'pressure {self.pressure}')
        # print(f'loaded: {part_type}, {pass_.sander}, {self.part_length}, {self.part_width},'
        #      f' {self.frame_width}, {self.__current_pass.hangover_value}, {self.__current_pass.overlap_value},'
        #      f' {self.__current_pass.speed_value}, {self.hold_back}')

    def slab(self):
        overhang_mm_x = self.__current_pass.hangover_value / 100 * self.sander_selection.get_x_value()
        overhang_mm_y = self.__current_pass.hangover_value / 100 * self.sander_selection.get_y_value()
        offset_x = self.sander_selection.get_x_value() / 2 - overhang_mm_x
        offset_y = self.sander_selection.get_y_value() / 2 - overhang_mm_y
        outside_box = overhang_mm_x + offset_x, overhang_mm_y + offset_y, self.part_length - overhang_mm_x - offset_x,\
                      self.part_width - overhang_mm_y - offset_y
        print(f'Outside box: {outside_box}')
        return outside_box

    def frame(self):
        # todo, look at changing the way we pass the frame info.  likely want to implement new strategy
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
            self.g_code.append(f'g0x-{center_positions[0][0]}y{center_positions[0][0]}')
            self.g_code.append(self.sander_selection.on(self.pressure))
            self.g_code.append(f'g1y{center_positions[1][1]}')
            self.g_code.append(f'g1x-{center_positions[2][0]}')
            self.g_code.append(f'g1y{center_positions[3][1]}')
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

    def panel_spiral_in(self, outside_box, perimeter, entire_panel=True, panel_offset=float):
        panel_offset = panel_offset * 25.4
        print(f'panel offset: {panel_offset}')
        if outside_box[2] >= outside_box[3]:
            
            y_half_width = ((outside_box[3] - outside_box[1]) / 2) + panel_offset # need to offset for center of panel
            print(self.sander_selection.get_y_value())
            passes = ceil(y_half_width / ((1 - float(self.__current_pass.overlap_value / 100)) * self.sander_selection.get_y_value()))
            print(f'x is longer than y, y half width : {y_half_width}, passes: {passes}')
            step_over_y = y_half_width / passes
            step_over_x = (self.sander_selection.get_x_value() * (1 - float(self.__current_pass.overlap_value / 100)))
        else:
            x_half_width = (outside_box[2] - outside_box[0]) / 2
            print(f'y is longer than x, x half width: {x_half_width}')
            # todo need to develop this logic

        self.g_code.append(self.sander_selection.get_offset())
        self.g_code.append(f'f{round(feed_speed_max * int(self.__current_pass.speed_value) / 100, 1)}')
        self.g_code.append(self.sander_selection.get_work_plane())
        # ramp in start, not currently ramping, but may not be necessary
        self.g_code.append(f'g0x-{round(outside_box[0] + (step_over_x *2), 1)}y{round(outside_box[3] - (step_over_y / 2) , 1)}')  # still working on this

        self.g_code.append(self.sander_selection.on(self.pressure))

        self.g_code.append(f'g1x-{round(outside_box[0], 1)}y{round(outside_box[3], 1)}(start)')  # start of box
        self.g_code.append(f'g1y{round(outside_box[1], 1)}(1)')
        self.g_code.append(f'g1x-{round(outside_box[2], 1)}(2)')
        self.g_code.append(f'g1y{round(outside_box[3], 1)}(3)')
        self.g_code.append(f'g1x-{round(outside_box[0], 1)}(end of perimeter)')

        if perimeter:
            # start at far side on y
            self.g_code.append(f'g1x-{round(outside_box[0], 1)}y{round(outside_box[3], 1)}(extra perimeter)')  # start of box
            self.g_code.append(f'g1y{round(outside_box[1], 1)}(1)')
            self.g_code.append(f'g1x-{round(outside_box[2], 1)}(2)')
            self.g_code.append(f'g1y{round(outside_box[3], 1)}(3)')
            self.g_code.append(f'g1x-{round(outside_box[0], 1)}(end of perimeter)')

        if entire_panel:
            self.g_code.append(
                f'g1x-{round(outside_box[0] + step_over_x, 1)}y{round(outside_box[3] - step_over_y, 1)}(before entering for loop)')

            for i in range(passes):
                self.g_code.append(f'g1x-{round(outside_box[2] - (step_over_x * (i+1)))}(1-{i + 1})')
                y_2_pass = round(outside_box[1] + (step_over_y * (i + 1)))
                self.g_code.append(f'g1y{y_2_pass}(2-{i + 1})')
                self.g_code.append(f'g1x-{round(outside_box[0] + step_over_x * (i+1))}(3-{i + 1})')
                self.g_code.append(f'g1y{round(outside_box[3] - (step_over_y * (i + 2)), 1)}(4-{i + 1})')
                if y_2_pass >= y_half_width:
                    break
            self.g_code.append(f'g1x-{outside_box[2] - step_over_x}(end)')

            self.g_code.append(self.sander_selection.off())

        return self.g_code

    def panel_parallel_x(self):
        """
        method to sand panels and slabs parallel on x
        """

    def panel_parallel_y(self):
        """
        method to sand panels and slabs parallel on y
        """

    def panel(self, panel_operation):
        print(f'panel operation: {panel_operation}')
        panel_x_dim = round(panel_operation[0] * 25.4, 1)
        panel_y_dim = round(panel_operation[1] * 25.4, 1)
        xpos = round(panel_operation[2] * 25.4, 1)
        ypos = round(panel_operation[3] * 25.4, 1)
        print(f'x: {panel_x_dim}, y: {panel_y_dim}, xpos: {xpos}, ypos: {ypos}')

        if self.sander_selection.get_y_value() >= (panel_y_dim + (self.frame_add * 2)):
            print('sander too wide')
            return None
        elif self.sander_selection.get_x_value() >= (panel_x_dim + (self.frame_add * 2)):
            print('sander too long')
            return None
        starting_boundary = xpos, ypos, panel_x_dim + xpos, panel_y_dim + ypos
        print(f'starting boundary: {starting_boundary}')
        offset_x = self.sander_selection.get_x_value() / 2 + self.frame_add
        offset_y = self.sander_selection.get_y_value() / 2 + self.frame_add
        outside_box = starting_boundary[0] + offset_x, starting_boundary[1] + offset_y, starting_boundary[2] - offset_x, starting_boundary[3] - offset_y
        print(f'Outside box: {outside_box}')
        return outside_box

    def end_cycle(self):
        buffer = []
        buffer.append('m5(deactivate vacuum)')
        buffer.append('g54(reset wco)')
        buffer.append(f'g0x-900y0(go to park position)')
        return buffer


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


def generate(sensors_board_ref=None, list_of_part_panel_info = None):
    door_style = db_utils.get_current_door_style()
    passes = db_utils.get_current_program()  # this object contain multiple paths
    zone = CustomMachineParamManager.get_value('side')
    # sensors_board_ref.turn_vacuum_on()
    # sensors_board_ref.send_vacuum_value(mode, param)
    if zone == 'left':
        # todo, part length and with is pulled from param manager, draw_utils should save there
        part_length = CustomMachineParamManager.get_value("left_part_length")
        part_width = CustomMachineParamManager.get_value("left_part_width")

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
        # print(f'length: {part_length} width: {part_width} type: {part_type}')
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

    all_g_codes = []
    for index, pass_ in enumerate(passes):
        print(f"pass no {index}")
        # todo, will need to modify this for new db info
        # part_type will need to be determined by new info, part length and width are the same?
        generate_code = SandingGenerate(pass_, door_style, part_length, part_width)
        part_type = False
        # print(f'list len {list_of_part_panel_info[1][0]}')
        if len(list_of_part_panel_info[1]) > 0:
            part_type = True
            list_1 = list_of_part_panel_info[1:]
            list_2 = list_1[0]
                                
        if part_type:  # if the part is a 5-piece
            if pass_.contain_frames:
                print("we are not handling frames yet")
                # generate_code.frame()
            if pass_.contain_panels:
                # will need for here for each panel that parts contain
                for panel_operation in list_2: # todo, pretty sure this is not correct
                    panel_outside_box = generate_code.panel(panel_operation)
                    panel_offset = panel_operation[3]
                    if panel_outside_box is not None:
                        generate_code.panel_spiral_in(panel_outside_box, pass_.make_extra_pass_around_perimeter, entire_panel=pass_.is_entire_panel, panel=panel_offset)
        else:  # the part is a slab
            if pass_.contain_slabs:
                outside_box = generate_code.slab()
                generate_code.panel_spiral_in(outside_box, pass_.make_extra_pass_around_perimeter, panel=0)
        all_g_codes.extend(generate_code.g_code)
        # all_g_codes.append("(the end of pass 1)")
    # todo add logic to turn off vacuum and park machine.

    """x_offset = max_length - part_length
    for each x-:
        old x - x_offset"""

    if zone == 'right':  # need to offset x dims by maximum length, and invert all x  todo
        for index, x in enumerate(all_g_codes):
            x_offset = CustomMachineParamManager.get_value('x_max_length') - part_length
            print(f'offset: {x_offset}')
            if x[0] == "g" and x[2] == "x":
                if x[3] == "-":
                    s = ""
                    for i in range(4, len(x)):
                        if x[i] in "0123456789.":
                            s += x[i]
                        else:
                            break
                    new_value = round(-1 * float(s) - x_offset, 2)
                    new_string = x[:3] + str(new_value) + x[i:]
                    all_g_codes[index] = new_string
                else:
                    all_g_codes[index] = x.replace("x", "x-")
                #  print(f"old: {x} new {all_g_codes[index]}")

    all_g_codes.extend(
        generate_code.end_cycle())  # todo the vacuum is releasing after the first run, need to figure out why
    f = open("g-code.nc", "w")
    for item in all_g_codes:
        f.write(item)
        f.write("\n")
    f.close()
    return all_g_codes

    # print(*all_g_codes, sep="\n")


if __name__ == "__main__":
    probe_test()
    #  generate()
