"""
script to generate g-code for cutting dovetail joints
this looks at the config.ini file and loads parameters, calculates g-code
and returns the g-code as a list.

created by: Jeremiah Lemon
4-10-2020
"""
import configparser
import os
import math
import sys
# from configurations.custom_pram_loader import CustomMachineParamManager

"""
i am establishing temporary variables to test the script


"""


class GenerateCode:
    def __init__(self):
        # general settings
        self.g_code = []
        self.pin_spacing = 25.4
        self.bit_height = 11.82
        self. distance_from_bottom = 5
        self.bitDiameter = 14
        self.bit_angle_rad = 7.5
        self.bit_angle = self.bit_angle_rad * (math.pi/180)
        self.materialThickness = 15
        self.left_active = 4
        self.right_active = 4

    def calculate(self):
        tan_test = math.tan(self.bit_angle)
        print(f'tangent test {tan_test}')
        pin_width = ((self.pin_spacing + ((self.bit_height * math.tan(self.bit_angle))*2))/2)-self.bitDiameter
        bit_taper = math.tan(self.bit_angle) * self.bit_height
        print(f'pin width {pin_width}')
        print(f'bit taper {bit_taper}')
        small_radius = round(pin_width/2, 4)
        print(f'small radius {small_radius}')
        large_radius = round((self.pin_spacing - pin_width) / 2, 2)
        print(f'large radius {large_radius}')
        straight_cut = self.materialThickness - (large_radius - (self.bitDiameter / 2)) - bit_taper
        print(f'straight cut {straight_cut}')
        starting_x = round(self.pin_spacing-(self.distance_from_bottom + (.5 * self.bitDiameter)), 4)
        print(f'starting point {starting_x}')
        depth = round(self.materialThickness - (large_radius -(self.bitDiameter/2))-bit_taper - 1, 4)
        print(f'depth {depth}')

        def dovetail_pattern():
            self.g_code.append('g91')
            self.g_code.append(f'g2x-{small_radius * 2}y0r{small_radius+.01}')
            self.g_code.append(f'g90')
            self.g_code.append(f'g1y{depth}')
            self.g_code.append('g91')
            self.g_code.append(f'g3x-{large_radius * 2}y0r{large_radius+.01}')
            self.g_code.append('g90')
            self.g_code.append(f'g1y-{depth}')

            # left cut
        if self.left_active != 0:
            self.g_code.append('g21')
            self.g_code.append('f1000')
            self.g_code.append(f"g0x-{starting_x}y-{self.materialThickness-self.bitDiameter}z-{self.bit_height}")
            self.g_code.append(f'g1y-{depth}')
            self.g_code.append('g91')
            self.g_code.append(f'g2x-{small_radius*2}y0r{small_radius+.01}')
            self.g_code.append(f'g90')
            self.g_code.append(f'g1y{depth}')
            self.g_code.append('g91')
            self.g_code.append(f'g3x-{large_radius*2}y0r{large_radius+.01}')
            self.g_code.append('g90')
            self.g_code.append(f'g1y-{depth}')
            dovetail_pattern()
            dovetail_pattern()

        # right cut
        if self.right_active != 0:
            pass

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
