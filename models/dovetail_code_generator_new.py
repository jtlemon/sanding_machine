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
from configurations.custom_pram_loader import CustomMachineParamManager

class GenerateCode:
    def __init__(self, joint_profile, bit_profile):
        # general settings
        self.left_active = self.config.getfloat('active side', 'leftactive')
        self.right_active = self.config.getfloat('active side', 'rightactive')
        self.bit_length = CustomMachineParamManager.get_value("bit_profile_diameter")
        self.g_code = []

    def calculate(self):


            # left cut
        if self.left_active != 0:
           pass

            # right cut
        if self.right_active != 0:
            pass

        return self.g_code


def main_mo():
    generate = GenerateCode()  # class instantiated
    f = open('test_g_code.nc', 'w')
    f.write('\n'.join(map(str, generate.calculate(300, 0, SAMPLE_PROFILE))))
    f.close()
    print("hello")

if __name__ == "__main__":
    main_mo()
