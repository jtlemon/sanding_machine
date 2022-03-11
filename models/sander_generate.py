"""
script to generate g-code for sanding machine
this looks at the config.ini file and loads parameters, calculates g-code
and returns the g-code as a list.

created by: Jeremiah Lemon
3-8-2022
"""

import os

try:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    from django.core.wsgi import get_wsgi_application

    application = get_wsgi_application()
except Exception as e:
    print(e)

from configurations.custom_pram_loader import CustomMachineParamManager
from models import db_utils
from apps.sanding_machine import models

"""
need to get all of the parameters from the current program

"""

feed_speed_max = 15000  # we probably want to move this to a static config file
x_max_length = 1778
y_max_width = 660.4
sander_on_delay = .5  # we probably want to move this to a static config file
sander_off_delay = .5  # we probably want to move this to a static config file

sander_dictionary = {1: {'on': 'm62', 'off': 'm63', 'extend': 'm70', 'retract': 'm71', 'offset': 'g55',
                         "x": 125, "y": 125},
                     2: {'on': 'm64', 'off': 'm65', 'extend': 'm72', 'retract': 'm73', 'offset': 'g56',
                         "x": 75, "y": 100},
                     3: {'on': 'm66', 'off': 'm67', 'extend': 'm74', 'retract': 'm75', 'offset': 'g57',
                         "x": 125, "y": 125},
                     4: {'on': 'm68', 'off': 'm69', 'extend': 'm78', 'retract': 'm79', 'offset': 'g58',
                         "x": 125, "y": 125}
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

        return f'{sander_dictionary[self._active_sander_id]["extend"]}' "\n" f'g4p{sander_on_delay}' "\n" \
               f'{sander_dictionary[self._active_sander_id]["on"]}m3s{pressure}'

    def off(self):
        if self._active_sander_id not in sander_dictionary:
            raise Exception("Sander ID is invalid")

        return f'{sander_dictionary[self._active_sander_id]["retract"]}m5' "\n" f'g4p{sander_off_delay}' \
               "\n" f'{sander_dictionary[self._active_sander_id]["off"]}'

    def get_x_value(self):
        return sander_dictionary[self._active_sander_id]['x']

    def get_y_value(self):
        return sander_dictionary[self._active_sander_id]['y']

    def get_offset(self):
        return sander_dictionary[self._active_sander_id]['offset']

    def map_pressure(self, x):
        in_min = 0
        in_max = 100
        out_min = CustomMachineParamManager.get_value("min_pressure")
        out_max = CustomMachineParamManager.get_value("max_pressure")
        shifted = int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)
        shifted2 = int((shifted - 0) * (100 - 0) / (30 - 0) + 0)
        return shifted2


class SandingGenerate:
    def __init__(self, part_type, pass_: models.SandingProgramPass, door_style: models.DoorStyle):

        self.g_code = []
        self.__current_pass = pass_
        self.sander_selection = SanderControl(pass_.sander)
        self._active_sander_id = pass_.sander.pk
        self.part_type = CustomMachineParamManager.get_value("")
        self.part_length = CustomMachineParamManager.get_value("part_length")
        self.part_width = CustomMachineParamManager.get_value("part_width")
        self.frame_width = door_style.get_value("outside_edge_width") + \
                           door_style.get_value("inside_edge_width") + \
                           door_style.get_value("frame_width")
        self.hold_back = door_style.get_value("hold_back_inside_edge")
        self.pressure = 10 *(self.sander_selection.map_pressure(self.__current_pass.pressure_value))
        print(f'pressure {self.pressure}')
        # print(f'loaded: {part_type}, {pass_.sander}, {self.part_length}, {self.part_width},'
        #      f' {self.frame_width}, {self.__current_pass.hangover_value}, {self.__current_pass.overlap_value},'
        #      f' {self.__current_pass.speed_value}, {self.hold_back}')

    def slab(self, perimeter):

        overhang_mm_x = self.__current_pass.hangover_value / 100 * self.sander_selection.get_x_value()
        print(f'overhang x :{overhang_mm_x}')
        overhang_mm_y = self.__current_pass.hangover_value / 100 * self.sander_selection.get_y_value()
        offset_x = self.sander_selection.get_x_value() / 2 - overhang_mm_x
        offset_y = self.sander_selection.get_y_value() / 2 - overhang_mm_y
        step_over_x = float(self.part_length) / (round(
            float(self.part_length) / (self.sander_selection.get_x_value() * float(
                self.__current_pass.overlap_value / 100))))
        step_over_y = float(self.part_width) / (round(
            float(self.part_width) / (self.sander_selection.get_y_value() * float(
                self.__current_pass.overlap_value / 100))))
        # print(offset_x)
        starting_position = offset_x, offset_y
        # print('you selected slab')
        self.g_code.append(self.sander_selection.get_offset())
        self.g_code.append(f'f{round(feed_speed_max * int(self.__current_pass.speed_value) / 100, 1)}')
        self.g_code.append('g17 g21')
        self.g_code.append(f'g0x-{round(starting_position[0] + step_over_x, 1)}z{round(starting_position[1], 1)}(ramp in)')
        self.g_code.append(self.sander_selection.on(self.pressure))
        self.g_code.append(f'g0x-{round(starting_position[0], 1)}z{round(starting_position[1], 1)}(start)')  # start pattern
          # updated to new
        self.g_code.append(f'g1z{round(float(self.part_width) - offset_y, 1)}(1)')
        self.g_code.append(f'g1x-{round(float(self.part_length) - offset_x, 1)}(2)')
        self.g_code.append(f'g1z{round(starting_position[1], 1)}(3)')
        if perimeter:
            self.g_code.append(f'g1x-{round(starting_position[0], 1)}z{round(starting_position[1], 1)}(start)')
            self.g_code.append(f'g1z{round(float(self.part_width) - offset_y, 1)}(1)')
            self.g_code.append(f'g1x-{round(float(self.part_length) - offset_x, 1)}(2)')
            self.g_code.append(f'g1z{round(starting_position[1], 1)}(3)')
            print('make extra pass')
            pass  # go around outside twice
        self.g_code.append(f'g1x-{round(starting_position[0] + step_over_x, 1)}(4)')
        passes = int(int(float(self.part_width) / step_over_y) / 2) - 1
        # print(f'passes: {passes}')
        for i in range(passes):
            self.g_code.append(f'g1z{round(float(self.part_width) - offset_y - (step_over_y * (i + 1)), 1)}(1-{i+1})')
            self.g_code.append(
                f'g1x-{round(float(self.part_length) - (starting_position[0] + (step_over_x * (i + 1))), 1)}(2-{i+1})')
            if i == passes - 1 and (passes % 2) == 0:
                break
            self.g_code.append(f'g1z{round(starting_position[1] + (step_over_y * (i + 1)), 1)}(3-{i+1})')
            self.g_code.append(f'g1x-{round(starting_position[0] + (step_over_x * (i + 2)), 1)}(4-{i+1})')
            if i == passes - 1:
                break
        self.g_code.append(self.sander_selection.off())
        self.g_code.append('g53g0x0z0')
        return self.g_code

    def frame(self):
        effective_sander_width = self.sander_selection.get_y_value() - (
                (self.sander_selection.get_y_value() * (self.__current_pass.hangover_value / 100)) * 2)
        print(f'effective width: {effective_sander_width}')
        if self.frame_width <= effective_sander_width:
            print('sand in one pass')
            start_position = self.frame_width / 2
            overhang_mm_x = self.__current_pass.hangover_value / 100 * self.sander_selection.get_x_value()
            overhang_mm_y = self.__current_pass.hangover_value / 100 * self.sander_selection.get_y_value()
            offset_x = float(self.sander_selection.get_x_value() / 2 - overhang_mm_x)
            offset_y = float(self.sander_selection.get_y_value() / 2 - overhang_mm_y)
            self.g_code.append(self.sander_selection.get_offset())
            self.g_code.append(f'f{round(feed_speed_max * int(self.__current_pass.speed_value) / 100, 1)}')
            self.g_code.append('g17 g21')
            self.g_code.append(f'g0x-{start_position}z{start_position}')
            self.g_code.append(self.sander_selection.on(self.pressure))
            self.g_code.append(f'g1x-{float(self.part_length) - offset_x}')
            self.g_code.append(f'g1z{float(self.part_width) - offset_y}')
            self.g_code.append(f'g1x-{start_position}')
            self.g_code.append(f'g1z{start_position}')
            self.g_code.append(self.sander_selection.off())
            self.g_code.append('g53g0x0z0')
        else:
            print('sand in two passes')

        print('you selected frame')
        return self.g_code

    def panel(self):
        stile = self.frame_width
        width = float(self.part_width)
        length = float(self.part_length)
        overlap = float(self.__current_pass.overlap_value)
        hold_back = float(self.hold_back)
        panel_size = length - (stile * 2), width - (stile * 2)
        panel_corners = (stile, stile), (stile, width - stile), (length - stile, width - stile), (length - stile, stile)
        print(panel_corners)
        step_over = length / (round(length / (self.sander_selection.get_x_value() * overlap / 100))), \
                    width / (round(width / (self.sander_selection.get_y_value() * overlap / 100)))
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
            ((panel_size[1] - hold_back) / step_over[1]) / 2) - 1  # i don't think i am calculating passes correctly
        print(f'panel start {panel_start}, passes: {passes}')
        self.g_code.append(self.sander_selection.get_offset())
        self.g_code.append(
            f'f{round(feed_speed_max * int(self.__current_pass.speed_value) / 10, 1)}')
        self.g_code.append('g17 g21')
        self.g_code.append(f'g0x-{panel_start[0]}z-{panel_start[1]}(starting)')
        self.g_code.append(self.sander_selection.on(self.pressure))
        self.g_code.append(f'g1x-{round(panel_corners[3][0] - offset_x, 1)}')
        self.g_code.append(f'g1z-{round(panel_corners[2][1] - offset_y, 1)}')
        self.g_code.append(f'g1x-{round(panel_start[0] + step_over[0], 1)}')
        for i in range(passes):
            self.g_code.append(f'g1z-{round(panel_corners[3][1] + offset_y + (step_over[1] * (i + 1)), 1)}(1-{i+1})')
            self.g_code.append(
                f'g1x-{round(float(length) - (panel_start[0] + (step_over[0] * (i + 1))), 1)}(2-{i+1})')
            if i == passes - 1 and (passes % 2) == 0: # break here if the number of passes was even
                break
            self.g_code.append(
                f'g1z-{round(panel_corners[2][1] - ((step_over[1]) * (i + 1 ) + offset_y), 1)}(3-{i+1})')
            self.g_code.append(f'g1x-{round(panel_start[0] + (step_over[0] * (i + 2)), 1)}(4-{i+1})')
            if i == passes - 1:
                break
            # todo break here if the number of passes was odd

        self.g_code.append(self.sander_selection.off())

        return self.g_code


def turn_vacuum_on(sensors_board_ref, ch):
    if sensors_board_ref is not None:
        sensors_board_ref.turn_vacuum_on(ch)
    else:
        print(f"debug mode turn on vacuum {ch}")


def turn_vacuum_off(sensors_board_ref, ch):
    if sensors_board_ref is not None:
        sensors_board_ref.turn_vacuum_off(ch)
    else:
        print(f"debug mode turn off vacuum {ch}")


def generate(sensors_board_ref=None):
    door_style = db_utils.get_current_door_style()
    passes = db_utils.get_current_program()  # this object contain multiple paths
    part_length = CustomMachineParamManager.get_value("part_length")
    part_width = CustomMachineParamManager.get_value("part_width")
    part_type = CustomMachineParamManager.get_value('left_slab_selected')
    print(f'part type: {part_type}')
    zone = CustomMachineParamManager.get_value('side')
    # sensors_board_ref.turn_vacuum_on()
    # sensors_board_ref.send_vacuum_value(mode, param)
    if zone == 'left':
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
        else:
            print('part is too short for work holding on x')
    if zone == 'right':
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
        generate_code = SandingGenerate(part_type, pass_, door_style)
        if part_type:  # if the part is a 5-piece
            print('5-piece')
            if pass_.contain_frames:
                print('frames')
                all_g_codes.extend(generate_code.frame())
            if pass_.contain_panels:
                all_g_codes.extend(generate_code.panel())
                print('panels')
        else:  # the part is a slab
            if pass_.contain_slabs:
                all_g_codes.extend(generate_code.slab(pass_.make_extra_pass_around_perimeter))
                print('slabs')
    print(*all_g_codes, sep="\n")
    return all_g_codes


if __name__ == "__main__":
    generate()
