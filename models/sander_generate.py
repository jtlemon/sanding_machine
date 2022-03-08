"""
script to generate g-code for sanding machine
this looks at the config.ini file and loads parameters, calculates g-code
and returns the g-code as a list.

created by: Jeremiah Lemon
3-8-2022
"""
# if you gonna work with the db just add these lines
import os

try:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    from django.core.wsgi import get_wsgi_application

    application = get_wsgi_application()
except Exception as e:
    print(e)

import math
import configurations.static_app_configurations
from configurations import MainConfigurationLoader
from configurations.custom_pram_loader import CustomMachineParamManager
from models import db_utils

"""
need to get all of the parameters from the current program

"""



feed_speed_max = 15000  # we probably want to move this to a static config file
sander_dictionary = {1: {'on': 'm62', 'off': 'm63', 'extend': 'm70', 'retract': 'm71', 'offset': 'g55',
                         "x": 125, "y": 125},
                     2: {'on': 'm64', 'off': 'm65', 'extend': 'm72', 'retract': 'm73', 'offset': 'g56',
                         "x": 75, "y": 100},
                     3: {'on': 'm66', 'off': 'm67', 'extend': 'm74', 'retract': 'm75', 'offset': 'g57',
                         "x": 125, "y": 125},
                     4: {'on': 'm68', 'off': 'm69', 'extend': 'm78', 'retract': 'm79', 'offset': 'g58',
                         "x": 125, "y": 125}
                     }

sander_on_delay = .5  # we probably want to move this to a static config file
sander_off_delay = .5  # we probably want to move this to a static config file


class Sander:
    def __init__(self):
        pass

    def on(self, active_sander):
        if not active_sander:
            raise Exception('Sander ID is required')
        if active_sander not in sander_dictionary:
            raise Exception("Sander ID is invalid")

        return f'{sander_dictionary[active_sander]["extend"]}' "\n" f'g4p{sander_on_delay}' "\n" f'{sander_dictionary[active_sander]["on"]}'

    def off(self, active_sander):
        if not active_sander:
            raise Exception('Sander ID is required')
        if active_sander not in sander_dictionary:
            raise Exception("Sander ID is invalid")

        return f'{sander_dictionary[active_sander]["retract"]}' "\n" f'g4p{sander_off_delay}' \
               "\n" f'{sander_dictionary[active_sander]["off"]}'


class SandingGenerate:
    def __init__(self):
        self.g_code = []
        self.active_tool = int(pass_one_dropdown.get())  #active tool will come from sanding program
        self.stile_width = float(50)  # todo stile width will come from active program
        self.sander_selection = Sander() # i don't think this will need changed

    def start(self, part_type):
        # print(f'size {width_entry.get()} x {length_entry.get()}, {stile_width_entry.get()}')

        # todo this function will need to change to get the part type from the combination of main toggle/and sanding program definition

        if part_type == 1:
            self.slab()
        elif part_type == 2:
            self.frame()
            self.panel()
        else:
            print('no style selected')
        return self.g_code
        # print('generate code')

    def slab(self):

        overhang_mm_x = overhang_slider.get() / 100 * sander_dictionary[self.active_tool]['x']  # todo get overhang from active sandpaper
        print(f'overhang x :{overhang_mm_x}')
        overhang_mm_y = overhang_slider.get() / 100 * sander_dictionary[self.active_tool]['y']  # todo get overhang from active sandpaper
        offset_x = sander_dictionary[self.active_tool]['x'] / 2 - overhang_mm_x
        offset_y = sander_dictionary[self.active_tool]['y'] / 2 - overhang_mm_y
        step_over_x = float(length_entry.get()) / (round(
            float(length_entry.get()) / (sander_dictionary[self.active_tool]['x'] * float(overlap_slider.get() / 100))))  # todo get overlap from active sandpaper
        step_over_y = float(width_entry.get()) / (round(
            float(width_entry.get()) / (sander_dictionary[self.active_tool]['y'] * float(overlap_slider.get() / 100))))  # todo get overlap from active sandpaper
        # print(offset_x)
        starting_position = offset_x, offset_y
        # print('you selected slab')
        self.g_code.append(sander_dictionary[self.active_tool]['offset'])
        self.g_code.append(f'f{round(feed_speed_max * int(speed_slider.get()) / 10, 1)}')
        self.g_code.append('g17 g21')
        self.g_code.append(f'g0x-{round(starting_position[0], 1)}z{round(starting_position[1], 1)}')  # start pattern
        self.g_code.append(self.sander_selection.on(self.active_tool))
        self.g_code.append(f'g1z{round(float(width_entry.get()) - offset_y, 1)}')
        self.g_code.append(f'g1x-{round(float(length_entry.get()) - offset_x, 1)}')
        self.g_code.append(f'g1z{round(starting_position[1], 1)}')
        self.g_code.append(f'g1x-{round(starting_position[0] + step_over_x, 1)}')
        passes = int(int(float(width_entry.get()) / step_over_y) / 2)
        # print(f'passes: {passes}')
        for i in range(passes):
            self.g_code.append(f'g1z{round(float(width_entry.get()) - offset_y - (step_over_y * (i + 1)), 1)}')
            self.g_code.append(
                f'g1x-{round(float(length_entry.get()) - (starting_position[0] + (step_over_x * (i + 1))), 1)}')
            if i == passes - 1:
                break
            self.g_code.append(f'g1z{round(starting_position[1] + (step_over_y * (i + 1)), 1)}')
            self.g_code.append(f'g1x-{round(starting_position[0] + (step_over_x * (i + 2)), 1)}')
        self.g_code.append(self.sander_selection.off(self.active_tool))
        self.g_code.append('g53g0x0z0')
        return self.g_code

    def frame(self):
        effective_sander_width = sander_dictionary[self.active_tool]['y'] - (
                    (sander_dictionary[self.active_tool]['y'] * (overhang_slider.get() / 100)) * 2)
        print(f'effective width: {effective_sander_width}')
        if self.stile_width <= effective_sander_width:
            print('sand in one pass')
            start_position = self.stile_width / 2
            overhang_mm_x = overhang_slider.get() / 100 * sander_dictionary[self.active_tool]['x']
            overhang_mm_y = overhang_slider.get() / 100 * sander_dictionary[self.active_tool]['y']
            offset_x = float(sander_dictionary[self.active_tool]['x'] / 2 - overhang_mm_x)
            offset_y = float(sander_dictionary[self.active_tool]['y'] / 2 - overhang_mm_y)
            self.g_code.append(sander_dictionary[self.active_tool]['offset'])
            self.g_code.append(f'f{round(feed_speed_max * int(speed_slider.get()) / 10, 1)}')
            self.g_code.append('g17 g21')
            self.g_code.append(f'g0x-{start_position}z{start_position}')
            self.g_code.append(self.sander_selection.on(self.active_tool))
            self.g_code.append(f'g1x-{float(length_entry.get()) - offset_x}')
            self.g_code.append(f'g1z{float(width_entry.get()) - offset_y}')
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
        width = float(width_entry.get())
        length = float(length_entry.get())
        overlap = float(overlap_slider.get())
        hold_back = float(hold_back_slider.get())
        panel_size = length - (stile / 2), width - (stile / 2)
        panel_corners = (stile, stile), (stile, width - stile), (length - stile, width - stile), (length - stile, stile)
        print(panel_corners)
        step_over = length / (round(length / (sander_dictionary[self.active_tool]['x'] * overlap / 100))),\
                    width / (round(width / (sander_dictionary[self.active_tool]['y'] * overlap / 100)))
        print(f'step over x : {step_over[0]} y: {step_over[1]}')
        offset_x = float(sander_dictionary[self.active_tool]['x']/2) + hold_back
        offset_y = float(sander_dictionary[self.active_tool]['y']/2) + hold_back
        print(f'panel size{panel_size}, offset: {offset_x, offset_y}')
        if sander_dictionary[self.active_tool]['y'] >= panel_size[1]:
            print('sander too wide')
        elif sander_dictionary[self.active_tool]['x'] >= panel_size[0]:
            print('sander too long')
        print('you selected panel')
        panel_start = self.stile_width + (float(sander_dictionary[self.active_tool]['x']) / 2) + \
                      hold_back_slider.get(), self.stile_width + \
                      (float(sander_dictionary[self.active_tool]['y']) / 2) + hold_back_slider.get()  # todo hold back will be coming from sanding program
        passes = int(((panel_size[1] - hold_back) / step_over[1]) / 2)
        print(f'panel start {panel_start}, passes: {passes}')
        self.g_code.append(sander_dictionary[self.active_tool]['offset'])
        self.g_code.append(f'f{round(feed_speed_max * int(speed_slider.get()) / 10, 1)}')  # todo speed will be coming from sanding program
        self.g_code.append('g17 g21')
        self.g_code.append(f'g0x-{panel_start[0]}z-{panel_start[1]}(starting)')
        self.g_code.append(self.sander_selection.on(self.active_tool))
        self.g_code.append(f'g1x-{round(panel_corners[3][0]- offset_x, 1)}')
        self.g_code.append(f'g1z-{round(panel_corners[2][1]- offset_y,1)}')
        self.g_code.append(f'g1x-{round(panel_start[0] + step_over[0], 1)}')
        for i in range(passes):
            self.g_code.append(f'g1z-{round(panel_corners[3][1]+ offset_y + (step_over[1] *(i + 1)),1)}(1)')
            self.g_code.append(
                f'g1x-{round(float(length_entry.get()) - (panel_start[0] + (step_over[0] * (i + 1))), 1)}(2)')  # length entry will be coming from main page length
            if i == passes - 1:
                break
            self.g_code.append(f'g1z-{round(panel_corners[2][1] + (step_over[1] + offset_y * (i + 1)), 1)}(3)')
            self.g_code.append(f'g1x-{round(panel_start[0] + (step_over[0] * (i + 2)), 1)}(4)')
        self.g_code.append(self.sander_selection.off(self.active_tool))

        return self.g_code


def generate():
    if int(pass_one_dropdown.get()) == 0:  # may not need this to validate...? we will be getting the pass from the sanding program
        print('no tool selected')
        return
    generate_code = SandingGenerate()  # this code will likely change to not save the g_code to file.
    f = open('g_code.nc', 'w')
    f.write('\n'.join(map(str, generate_code.start(style.get()))))  # this is passing style, which will come from main page toggle
    f.close()
    print(*generate_code.g_code, sep="\n")



"""

the following code is old code from the dovetail generate i have left it here for reference
class GenerateCode:
    def __init__(self):
        # general settings
        self.g_code = []
        self.left_active = 25.4 * (CustomMachineParamManager.get_value("left_active"))
        self.right_active = 25.4 * (CustomMachineParamManager.get_value("right_active"))
        self.x_offset = CustomMachineParamManager.get_value("dovetail_setting_x_zero")
        self.y_offset = CustomMachineParamManager.get_value("dovetail_setting_y_zero")
        self.z_offset = CustomMachineParamManager.get_value("dovetail_setting_z_zero")
        self.fence_offset = CustomMachineParamManager.get_value("dovetail_fence_distance")
        print(f'offsets {self.x_offset}, {self.y_offset}, {self.z_offset}')

    def set_fences(self):

        if db_utils.is_joint_selected():
            fence_offset = CustomMachineParamManager.get_value("joint_profile_pin_spacing") / 2
            print(f'fence offset: {fence_offset}')
            left_fence_position = CustomMachineParamManager.get_value("dovetail_setting_a_zero") - fence_offset
            right_fence_position = CustomMachineParamManager.get_value("dovetail_setting_b_zero") - fence_offset
            print(f'fence positions: {left_fence_position}, {right_fence_position}')
            self.g_code.append(f'g0a-{left_fence_position}b-{right_fence_position}')
            return self.g_code
        elif db_utils.is_dowel_selected():
            print('setting upper fences')
            left_fence_position = CustomMachineParamManager.get_value("dovetail_setting_a_zero")
            right_fence_position = CustomMachineParamManager.get_value("dovetail_setting_b_zero")
            self.g_code.append(f'g0a-{left_fence_position}b-{right_fence_position}')
            return self.g_code

    def calculate(self):
        def drill_locations():
            self.g_code.append('g0z0')
            drill_hole_left()
            drill_hole_right()
            self.g_code.append('g0z0y0')

        def drill_hole_left():
            number_of_holes = (math.ceil((self.left_active-distance_from_edge) / spacing))
            points = []
            for i in range(number_of_holes):
                points.append(distance_from_edge + i * spacing)
            for i in list(points):
                self.g_code.append(f'g0x-{self.x_offset + i}y-{self.y_offset - distance_from_face}')
                self.g_code.append(f'g0z-{z_drill_depth_edge}')
                self.g_code.append(f'g0z-{z_drill_zero}')
                self.g_code.append(f'g0y-{self.y_offset + distance_from_face}')
                self.g_code.append(f'g0z-{z_drill_depth_face}')
                self.g_code.append(f'g0z-{z_drill_zero}')

        def drill_hole_right():
            number_of_holes = (math.ceil((self.right_active - distance_from_edge)/ spacing))
            points = []
            for i in range(number_of_holes):
                points.append(distance_from_edge + i * spacing)
            right_offset = self.fence_offset + self.x_offset
            for i in list(points):
                self.g_code.append(f'g0x-{right_offset - i}y-{self.y_offset - distance_from_face}')
                self.g_code.append(f'g0z-{z_drill_depth_edge}')
                self.g_code.append(f'g0z-{z_drill_zero}')
                self.g_code.append(f'g0y-{self.y_offset + distance_from_face}')
                self.g_code.append(f'g0z-{z_drill_depth_face}')
                self.g_code.append(f'g0z-{z_drill_zero}')

        def dovetail_score_cut(x_score_cut):
            self.g_code.append('g90')
            self.g_code.append(
                f'g0x-{x_score_cut + self.left_active}y-{self.y_offset - depth - large_radius + depth_adjustment}z-{z_cut_height}')  # needs depth adjustment
            self.g_code.append(f'g1x-{x_score_cut}f{loaded_bit_feed_speed}')
            pass

        def dovetail_pre_position():
            self.g_code.append('g91')
            self.g_code.append(f'g1y-{depth + large_radius}')

        def dovetail_pattern():
            number_of_cuts = (math.ceil(self.left_active / loaded_pin_spacing))
            for i in range(number_of_cuts):
                self.g_code.append('g91')
                self.g_code.append(f'g2x-{small_radius * 2}y0r{small_radius + .01}')
                self.g_code.append(f'g1y{depth}')
                self.g_code.append(f'g3x-{large_radius * 2}y0r{large_radius + .01}')
                self.g_code.append(f'g1y-{depth}')

            self.g_code.append(f'g2x-{small_radius * 2}y0r{small_radius + .01}')
            self.g_code.append('g90')
            self.g_code.append('g1y-0')  # retracting a lot further than needed, find strategy to not retract so far.

        if db_utils.is_joint_selected():
            loaded_joint_profile = db_utils.get_loaded_joint_profile()
            print('dovetail joint')
            # create joint variables
            joint_deep_adjustment = loaded_joint_profile.get_value("joint_deep_adjustment")
            loaded_bit = db_utils.get_loaded_bit_profile()
            loaded_pin_spacing = loaded_joint_profile.get_value("joint_profile_pin_spacing")
            loaded_material_thickness = loaded_joint_profile.get_value("joint_profile_material_thickness")
            loaded_bit_height = loaded_joint_profile.get_value("joint_profile_bit_height")
            loaded_distance_from_bottom = loaded_joint_profile.get_value("joint_profile_distance_from_bottom")
            width_adjustment = loaded_joint_profile.get_value("joint_tightness_adjustment")
            depth_adjustment = loaded_joint_profile.get_value("joint_deep_adjustment")
            print(f'width adjustment{width_adjustment} depth adjustment {depth_adjustment}')

            # create bit variables
            loaded_bit_diameter = loaded_bit.get_value("bit_profile_diameter")
            loaded_bit_feed_speed = loaded_bit.get_value("bit_profile_feed_speed")
            loaded_bit_angle_rad = loaded_bit.get_value("bit_profile_angle")
            loaded_bit_offset = CustomMachineParamManager.get_value("loaded_bit_length") * - 1  # needs bit offset
            print(f'loaded bit length {loaded_bit_offset}')

            # calculate cutting params
            z_cut_height = loaded_bit_height + loaded_bit_offset + self.z_offset
            bit_angle = loaded_bit_angle_rad * (math.pi / 180)
            pin_width = ((loaded_pin_spacing + (
                    (loaded_bit_height * math.tan(bit_angle)) * 2)) / 2) - loaded_bit_diameter
            bit_taper = math.tan(bit_angle) * loaded_bit_height
            print(f'pin width {pin_width}')
            small_radius = round((pin_width / 2) + width_adjustment, 4)

            large_radius = round(((loaded_pin_spacing - pin_width) / 2) - width_adjustment, 3)
            print(f'small radius {small_radius}, large radius {large_radius}')
            straight_cut = loaded_material_thickness - (large_radius - (loaded_bit_diameter / 2)) - bit_taper
            starting_x = round(
                (loaded_pin_spacing - (loaded_distance_from_bottom + (.5 * loaded_bit_diameter)) + self.x_offset), 4)
            depth = round((loaded_material_thickness - (
                        large_radius - (loaded_bit_diameter / 2)) - bit_taper - 1) - depth_adjustment, 4)

            if self.left_active != 0:
                # perform cuts
                dovetail_score_cut(starting_x)
                dovetail_pre_position()
                dovetail_pattern()

            if self.right_active != 0:
                dovetail_score_cut(starting_x + self.fence_offset - self.right_active)
                dovetail_pre_position()
                dovetail_pattern()

            self.g_code.append('g90')
            self.g_code.append('g0x-300')

        elif db_utils.is_dowel_selected():
            loaded_joint_profile = db_utils.get_loaded_dowel_profile()
            print('dowel joint')
            # else:
            print("this means dowel profile selected")

            loaded_bit = db_utils.get_loaded_bit_profile()
            print(f'loaded bit: {loaded_bit}')
            distance_from_edge = loaded_joint_profile.get_value("dowel_profile_dis_from_edge")
            spacing = loaded_joint_profile.get_value("dowel_profile_spacing")
            distance_from_face = loaded_joint_profile.get_value("dowel_profile_dis_from_face")
            face_depth = loaded_joint_profile.get_value("dowel_profile_face_depth")
            edge_depth = loaded_joint_profile.get_value("dowel_profile_edge_depth")
            loaded_bit_offset = CustomMachineParamManager.get_value("loaded_bit_length") * - 1
            z_drill_zero = loaded_bit_offset + self.z_offset - 5
            z_drill_depth_face = loaded_bit_offset + self.z_offset + face_depth
            z_drill_depth_edge = loaded_bit_offset + self.z_offset + edge_depth
            print(f'params: {distance_from_edge}, {spacing}, {distance_from_face}, {face_depth}, {edge_depth}')

            if self.left_active != 0:
                drill_locations()
            #  place code for drill here.

        else:
            raise ValueError("you have to select a profile first")

        return self.g_code

    def locating_bar(self, state):
        if state:
            self.g_code.append('m62')
        else:
            self.g_code.append('m63')

    def left_upper_clamp(self, state):
        if state:
            self.g_code.append('m64')
        else:
            self.g_code.append('m65')

    def right_upper_clamp(self, state):
        if state:
            self.g_code.append('m66')
        else:
            self.g_code.append('m67')

    def left_lower_clamp(self, state):
        if state:
            self.g_code.append('m68')
        else:
            self.g_code.append('m69')

    def right_lower_clamp(self, state):
        if state:
            self.g_code.append('m70')
        else:
            self.g_code.append('m71')


def main_mo():
    generate = GenerateCode()  # class instantiated
    f = open('test_g_code.nc', 'w')
    f.write('\n'.join(map(str, generate.calculate())))
    f.close()
    print(*generate.g_code, sep="\n")
"""

if __name__ == "__main__":
    generate()
