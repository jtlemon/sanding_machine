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
        self.left_active = CustomMachineParamManager.get_value("left_active")
        self.right_active = CustomMachineParamManager.get_value("right_active")

    def calculate(self):
        def dovetail_score_cut():
            pass

        def dovetail_pre_position():
            self.g_code.append('g21')
            self.g_code.append(f'f{loaded_bit_feed_speed}')
            self.g_code.append(
                f"g0x-{starting_x}y-{loaded_material_thickness - loaded_bit_diameter}z-{loaded_bit_height}")
            self.g_code.append(f'g1y-{depth}')
            self.g_code.append('g91')
            self.g_code.append(f'g2x-{small_radius * 2}y0r{small_radius + .01}')
            self.g_code.append(f'g90')
            self.g_code.append(f'g1y{depth}')
            self.g_code.append('g91')
            self.g_code.append(f'g3x-{large_radius * 2}y0r{large_radius + .01}')
            self.g_code.append('g90')
            self.g_code.append(f'g1y-{depth}')
            
        def dovetail_pattern():
            number_of_cuts = (math.ceil(self.left_active / loaded_pin_spacing))
            for i in range(number_of_cuts):
                self.g_code.append('g91')
                self.g_code.append(f'g2x-{small_radius * 2}y0r{small_radius + .01}')
                self.g_code.append(f'g90')
                self.g_code.append(f'g1y{depth}')
                self.g_code.append('g91')
                self.g_code.append(f'g3x-{large_radius * 2}y0r{large_radius + .01}')
                self.g_code.append('g90')
                self.g_code.append(f'g1y-{depth}')

        loaded_joint_profile = db_utils.get_loaded_joint_profile()
        if CustomMachineParamManager.get_value("joint_type", "joint_profile") == "joint_profile":
            # create joint variables
            joint_deep_adjustment = loaded_joint_profile.get_value("joint_deep_adjustment")
            loaded_bit = db_utils.get_loaded_bit_profile()
            x = loaded_joint_profile.get_value("bit_profile_diameter")
            loaded_pin_spacing = loaded_joint_profile.get_value("joint_profile_pin_spacing")
            loaded_material_thickness = loaded_joint_profile.get_value("joint_profile_material_thickness")
            loaded_bit_height = loaded_joint_profile.get_value("joint_profile_bit_height")
            loaded_distance_from_bottom = loaded_joint_profile.get_value("joint_profile_distance_from_bottom")

            # create bit variables
            loaded_bit_diameter = loaded_bit.get_value("bit_profile_diameter")
            loaded_bit_feed_speed = loaded_bit.get_value("bit_profile_feed_speed")
            loaded_bit_angle_rad = loaded_bit.get_value("bit_profile_angle")
            # calculate cutting params
            bit_angle = loaded_bit_angle_rad * (math.pi / 180)
            tan_test = math.tan(bit_angle)
            print(f'tangent test {tan_test}')
            pin_width = ((loaded_pin_spacing + (
                    (loaded_bit_height * math.tan(bit_angle)) * 2)) / 2) - loaded_bit_diameter
            bit_taper = math.tan(bit_angle) * loaded_bit_height
            print(f'pin width {pin_width}')
            print(f'bit taper {bit_taper}')
            small_radius = round(pin_width / 2, 4)
            print(f'small radius {small_radius}')
            large_radius = round((loaded_pin_spacing - pin_width) / 2, 2)
            print(f'large radius {large_radius}')
            straight_cut = loaded_material_thickness - (large_radius - (loaded_bit_diameter / 2)) - bit_taper
            print(f'straight cut {straight_cut}')
            starting_x = round(loaded_pin_spacing - (loaded_distance_from_bottom + (.5 * loaded_bit_diameter)), 4)
            print(f'starting point {starting_x}')
            depth = round(loaded_material_thickness - (large_radius - (loaded_bit_diameter / 2)) - bit_taper - 1, 4)
            print(f'depth {depth}')

            if self.left_active != 0:
                # perform cuts
                dovetail_score_cut()
                dovetail_pre_position()
                dovetail_pattern()

            if self.right_active != 0:
                pass

        else:
            print("this means dowel profile selected")
            #  place code for drill here.

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
