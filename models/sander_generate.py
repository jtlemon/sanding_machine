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
from models.machine_models.sanding_generate import SandingGenerate
from models.machine_models.utils import *


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
