"""
script to generate g-code for cutting dovetail joints
this looks at the config.ini file and loads parameters, calculates g-code
and returns the g-code as a list.

created by: Jeremiah Lemon
4-10-2020
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
i am establishing temporary variables to test the script


"""


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

    def calculate(self):
        def drill_locations():
            self.g_code.append('g0z0')
            self.g_code.append(f'g0x-{self.x_offset + distance_from_edge}y-{self.y_offset-distance_from_face}')
            self.g_code.append(f'g0z-{z_drill_zero}')
            self.g_code.append('g0z0')
            self.g_code.append(f'g0x-{self.x_offset + distance_from_edge}y-{self.y_offset + distance_from_face}')
            self.g_code.append(f'g0z-{z_drill_zero}')
            self.g_code.append('g0z0')
            self.g_code.append('g0z0y0')
            drill_hole()

        def drill_hole():
            number_of_holes = (math.ceil(self.left_active / spacing)) - 1
            print(f'# holes: {number_of_holes}')
            for i in range(number_of_holes):

                print('for statement')

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
            z_drill_zero = loaded_bit_offset + self.z_offset
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


if __name__ == "__main__":
    main_mo()
