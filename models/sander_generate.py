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
    def __init__(self, sander_db_obj:models.Sander):
        self._active_sander_id = sander_db_obj.pk
        self._sander_db_obj = sander_db_obj

    def on(self):
        if self._active_sander_id not in sander_dictionary:
            raise Exception("Sander ID is invalid")
        # put the logic

        x_sander = self._sander_db_obj.x_length


        return f'{sander_dictionary[self._active_sander_id]["extend"]}' "\n" f'g4p{sander_on_delay}' "\n" f'{sander_dictionary[self._active_sander_id]["on"]}'

    def off(self):
        if self._active_sander_id not in sander_dictionary:
            raise Exception("Sander ID is invalid")

        return f'{sander_dictionary[self._active_sander_id]["retract"]}' "\n" f'g4p{sander_off_delay}' \
               "\n" f'{sander_dictionary[self._active_sander_id]["off"]}'

    def get_x_value(self):
        return sander_dictionary[self._active_sander_id]['x']

    def get_y_value(self):
        return sander_dictionary[self._active_sander_id]['y']

class SandingGenerate:
    def __init__(self, part_type, pass_:models.SandingProgramPass, door_style:models.DoorStyle):

        self.g_code = []
        self.__current_pass = pass_
        self.sander_selection = SanderControl(pass_.sander)  # i don't think this will need changed
        self.part_type = part_type
        self.part_length = CustomMachineParamManager.get_value("part_length")
        self.part_width = CustomMachineParamManager.get_value("part_width")
        self.frame_width = door_style.get_value("outside_edge_width") + \
                           door_style.get_value("inside_edge_width") +\
                           door_style.get_value("frame_width")
        print(f'loaded: {part_type}, {pass_.sander}, {self.part_length}, {self.part_width},'
              f' {self.frame_width}, {self.__current_pass.hangover_value}, {self.__current_pass.overlap_value},'
              f' {self.__current_pass.speed_value}, {door_style.get_value("hold_back_inside_edge")}')

    def start(self):

        # todo this function will need to change to get the part type from the combination of main toggle/and sanding program definition
        if not self.part_type:
            self.slab()
        elif self.part_type:
            self.frame()
            self.panel()
        else:
            print('no style selected')
        return self.g_code
        # print('generate code')

    def slab(self):

        overhang_mm_x = self.__current_pass.hangover_value / 100 * sander_dictionary[self.active_tool][
            'x']  # todo get overhang from active sandpaper
        print(f'overhang x :{overhang_mm_x}')
        overhang_mm_y = self.__current_pass.hangover_value / 100 * sander_dictionary[self.active_tool][
            'y']  # todo get overhang from active sandpaper
        offset_x = sander_dictionary[self.active_tool]['x'] / 2 - overhang_mm_x
        offset_y = sander_dictionary[self.active_tool]['y'] / 2 - overhang_mm_y
        step_over_x = float(self.part_length) / (round(
            float(self.part_length) / (self.sander_selection.get_x_value() * float(
                self.overlap / 100))))  # todo get overlap from active sandpaper
        step_over_y = float(self.part_width) / (round(
            float(self.part_width) / (sander_dictionary[self.active_tool]['y'] * float(
                self.overlap / 100))))  # todo get overlap from active sandpaper
        # print(offset_x)
        starting_position = offset_x, offset_y
        # print('you selected slab')
        self.g_code.append(sander_dictionary[self.active_tool]['offset'])
        self.g_code.append(f'f{round(feed_speed_max * int(self.speed) / 10, 1)}')
        self.g_code.append('g17 g21')
        self.g_code.append(f'g0x-{round(starting_position[0], 1)}z{round(starting_position[1], 1)}')  # start pattern
        self.g_code.append(self.sander_selection.on(self.active_tool))
        self.g_code.append(f'g1z{round(float(self.part_width) - offset_y, 1)}')
        self.g_code.append(f'g1x-{round(float(self.part_length) - offset_x, 1)}')
        self.g_code.append(f'g1z{round(starting_position[1], 1)}')
        self.g_code.append(f'g1x-{round(starting_position[0] + step_over_x, 1)}')
        passes = int(int(float(self.part_width) / step_over_y) / 2)
        # print(f'passes: {passes}')
        for i in range(passes):
            self.g_code.append(f'g1z{round(float(self.part_width) - offset_y - (step_over_y * (i + 1)), 1)}')
            self.g_code.append(
                f'g1x-{round(float(self.part_length) - (starting_position[0] + (step_over_x * (i + 1))), 1)}')
            if i == passes - 1:
                break
            self.g_code.append(f'g1z{round(starting_position[1] + (step_over_y * (i + 1)), 1)}')
            self.g_code.append(f'g1x-{round(starting_position[0] + (step_over_x * (i + 2)), 1)}')
        self.g_code.append(self.sander_selection.off(self.active_tool))
        self.g_code.append('g53g0x0z0')
        return self.g_code

    def frame(self):
        effective_sander_width = sander_dictionary[self.active_tool]['y'] - (
                (sander_dictionary[self.active_tool]['y'] * (self.overhang / 100)) * 2)
        print(f'effective width: {effective_sander_width}')
        if self.frame_width <= effective_sander_width:
            print('sand in one pass')
            start_position = self.frame_width / 2
            overhang_mm_x = self.overhang / 100 * sander_dictionary[self.active_tool]['x']
            overhang_mm_y = self.overhang / 100 * sander_dictionary[self.active_tool]['y']
            offset_x = float(sander_dictionary[self.active_tool]['x'] / 2 - overhang_mm_x)
            offset_y = float(sander_dictionary[self.active_tool]['y'] / 2 - overhang_mm_y)
            self.g_code.append(sander_dictionary[self.active_tool]['offset'])
            self.g_code.append(f'f{round(feed_speed_max * int(self.speed) / 10, 1)}')
            self.g_code.append('g17 g21')
            self.g_code.append(f'g0x-{start_position}z{start_position}')
            self.g_code.append(self.sander_selection.on(self.active_tool))
            self.g_code.append(f'g1x-{float(self.part_length) - offset_x}')
            self.g_code.append(f'g1z{float(self.part_width) - offset_y}')
            self.g_code.append(f'g1x-{start_position}')
            self.g_code.append(f'g1z{start_position}')
            self.g_code.append(self.sander_selection.off(self.active_tool))
            self.g_code.append('g53g0x0z0')
        else:
            print('sand in two passes')

        print('you selected frame')
        return self.g_code

    def panel(self):
        stile = self.stile_width
        width = float(self.part_width)
        length = float(self.part_length)
        overlap = float(self.overlap)
        hold_back = float(hold_back_slider.get())
        panel_size = length - (stile / 2), width - (stile / 2)
        panel_corners = (stile, stile), (stile, width - stile), (length - stile, width - stile), (length - stile, stile)
        print(panel_corners)
        step_over = length / (round(length / (sander_dictionary[self.active_tool]['x'] * overlap / 100))), \
                    width / (round(width / (sander_dictionary[self.active_tool]['y'] * overlap / 100)))
        print(f'step over x : {step_over[0]} y: {step_over[1]}')
        offset_x = float(sander_dictionary[self.active_tool]['x'] / 2) + hold_back
        offset_y = float(sander_dictionary[self.active_tool]['y'] / 2) + hold_back
        print(f'panel size{panel_size}, offset: {offset_x, offset_y}')
        if sander_dictionary[self.active_tool]['y'] >= panel_size[1]:
            print('sander too wide')
        elif sander_dictionary[self.active_tool]['x'] >= panel_size[0]:
            print('sander too long')
        print('you selected panel')
        panel_start = self.stile_width + (float(sander_dictionary[self.active_tool]['x']) / 2) + \
                      hold_back_slider.get(), self.stile_width + \
                      (float(sander_dictionary[self.active_tool][
                                 'y']) / 2) + hold_back_slider.get()  # todo hold back will be coming from sanding program
        passes = int(((panel_size[1] - hold_back) / step_over[1]) / 2)
        print(f'panel start {panel_start}, passes: {passes}')
        self.g_code.append(sander_dictionary[self.active_tool]['offset'])
        self.g_code.append(
            f'f{round(feed_speed_max * int(speed_slider.get()) / 10, 1)}')  # todo speed will be coming from sanding program
        self.g_code.append('g17 g21')
        self.g_code.append(f'g0x-{panel_start[0]}z-{panel_start[1]}(starting)')
        self.g_code.append(self.sander_selection.on(self.active_tool))
        self.g_code.append(f'g1x-{round(panel_corners[3][0] - offset_x, 1)}')
        self.g_code.append(f'g1z-{round(panel_corners[2][1] - offset_y, 1)}')
        self.g_code.append(f'g1x-{round(panel_start[0] + step_over[0], 1)}')
        for i in range(passes):
            self.g_code.append(f'g1z-{round(panel_corners[3][1] + offset_y + (step_over[1] * (i + 1)), 1)}(1)')
            self.g_code.append(
                f'g1x-{round(float(length) - (panel_start[0] + (step_over[0] * (i + 1))), 1)}(2)')  # length entry will be coming from main page length
            if i == passes - 1:
                break
            self.g_code.append(f'g1z-{round(panel_corners[2][1] + (step_over[1] + offset_y * (i + 1)), 1)}(3)')
            self.g_code.append(f'g1x-{round(panel_start[0] + (step_over[0] * (i + 2)), 1)}(4)')
        self.g_code.append(self.sander_selection.off(self.active_tool))

        return self.g_code


def generate():
    door_style = db_utils.get_current_door_style()
    passes = db_utils.get_current_program()  # this object contain multiple paths
    frame_width = door_style.get_value("frame_width") # this needs to get calculated
    # determine left or right zone
    part_length = CustomMachineParamManager.get_value("part_length")
    part_width = CustomMachineParamManager.get_value("part_width")
    part_type = CustomMachineParamManager.get_value('left_slap_selected')
    holdback = door_style.get_value("hold_back_inside_edge")
    zone = CustomMachineParamManager.get_value('side')
    print(f'part width: {part_width}, {frame_width}')

    print(f'part type: {part_type}')
    # determine which vacuum pods to turn on based on part width and length
    # for each pass, generate g-code
    if zone == 'left':
        if part_length >= 1488:
            print('turn on vacuum pod 6')
        elif part_length >= 950:
            print('turn on vacuum pod 5')
        elif part_length >= 700:
            print('turn on vacuum pod 4')
        elif part_length >= 300:
            print('turn on vacuum pod 3')
        else:
            print('part is too short for work holding on x')

        if part_width >= 360:
            print('turn on vacuum pod 1')
        elif part_width >= 135:
            print('turn on vacuum pod 2')
        else:
            print('part is too short for work holding on x')
    if zone == 'right':
        if part_length >= 700:
            print('turn on vacuum pod 5')
        elif part_length >= 300:
            print('turn on vacuum pod 6')
        else:
            print('part is too short for work holding on x')

        if part_width >= 360:
            print('turn on vacuum pod 8')
        elif part_width >= 135:
            print('turn on vacuum pod 7')
        else:
            print('part is too short for work holding on x')
        # todo need a strategy to apply a compensation for right,
        # 1: change x0 to left end of piece, then send the same program we send for left zone
        # 2:
    all_g_codes = []
    for index, pass_ in enumerate(passes):
        print(f"pass no {index}")
        generate_code = SandingGenerate(part_type,  pass_, door_style)
        all_g_codes.extend(generate_code.start())

    """  
    
    if int(pass_one_dropdown.get()) == 0:  # may not need this to validate...? we will be getting the pass from the sanding program
        print('no tool selected')
        return
    generate_code = SandingGenerate()  # this code will likely change to not save the g_code to file.
    f = open('g_code.nc', 'w')
    f.write('\n'.join(map(str, generate_code.start(style.get()))))  # this is passing style, which will come from main page toggle
    f.close()
    print(*generate_code.g_code, sep="\n")
    """


if __name__ == "__main__":
    generate()
