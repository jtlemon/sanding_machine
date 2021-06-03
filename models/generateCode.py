"""
script to generate g-code for cutting dovetail joints
this looks at the config.ini file and loads parameters, calculates g-code
and returns the g-code as a list.

created by: Jeremiah Lemon
4-10-2020

1-17-2020 updates:
needs to change to using joint profiles,  currently the height(Y axis), depth(Z axis), dowel protrusion(A axis), inject, and insert for
 each hole is set the same for the entire pattern of holes.  these parameters need to be set individually for each hole
 with the info from the joint settings profile table
 the dowel position is the X axis coordinate

"""
import configparser
import os
import scipy.interpolate
import ast
from PySide2 import QtCore
from configurations import MainConfigurationLoader

class GenerateCode(QtCore.QObject):
    startupSignal = QtCore.Signal()
    def __init__(self):
        super(GenerateCode, self).__init__()
        # general settings
        self.spindle_speed = MainConfigurationLoader.get_spindle_speed_value()  # stays, set once for entire program
        self.feed_speed = MainConfigurationLoader.get_feed_speed_value()  # stays, set once for entire program
        self.left_x_zero = MainConfigurationLoader.get_left_xzero_value()  # stays, set once for entire program
        self.y_zero = MainConfigurationLoader.get_y_zero_value()  # stays, set once for entire program
        self.z_zero = MainConfigurationLoader.get_z_zero_value()  # stays, set once for entire program
        self.dowel_protrusion_zero = MainConfigurationLoader.get_dowel_protrusion_offset_value()  # stays, set once for entire program
        self.z_retract = MainConfigurationLoader.get_z_retract_distance_value() # stays, set once for entire program
        self.drill_insert_offset = MainConfigurationLoader.get_drill_to_insert_offset_value() # stays, set once for entire program
        self.drill_insert_height_offset = MainConfigurationLoader.get_drill_to_insert_height_offset_value() # stays, set once for entire program
        self.injection_time = MainConfigurationLoader.get_water_injection_time_value() # stays, set once for entire program
        self.insertion_time = MainConfigurationLoader.get_dowel_insertion_time_value() # stays, set once for entire program
        self.insertion_delay = MainConfigurationLoader.get_dowel_insertion_delay_value() # stays, set once for entire program
        self.dowel_release_time = MainConfigurationLoader.get_dowel_release_time_value() # stays, set once for entire program
        self.back_distance = MainConfigurationLoader.get_distance_from_backedge_value() # stays, set once for entire program
        self.fence_distance = MainConfigurationLoader.get_distance_between_fences_value() # stays, set once for entire program

        self.g_code = []

        """
        the following section is for interpolation of the table top variations.  every time a move is made to 
        an x coordinate to drill a hole, or insert a dowel, the the interpolation is performed to find the Y axis deviation
        needed to match table top variations.
        """
        x = [0, 50, 100, 150, 200, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900, 950, 1000, 1050]
        y = MainConfigurationLoader.get_table_variations_readings()
        print(len(x), len(y))
        self.y_interpolate = scipy.interpolate.interp1d(x, y)

    def calculate(self, left_part, right_part, dowels_profiles={}):
        self.startup()
        if left_part != 0:
            self.left_clamp(left_part)
        if right_part != 0:
            self.right_clamp(right_part)

        # left cut
        if left_part != 0:
            self.left_cut_new(left_part, 'forward', dowels_profiles)
            self.release_left_clamp(left_part)

        # right cut
        if right_part != 0:
            self.right_cut_new(right_part, 'forward', dowels_profiles)
            self.release_right_clamp(right_part)
            # @TODO  what the value of self.hole_start should be
            #self.g_code.append(f'g0x-{self.left_x_zero + self.hole_start :.2f}(move to left park)')
        self.end_cycle()
        return self.g_code

    def drill_hole(self, hole_depth):
        rapid_depth = self.z_zero
        drill_depth = self.z_zero + self.z_retract + hole_depth
        start_depth = self.z_zero + self.z_retract
        # self.g_code.append(f'g0z-{rapid_depth}(starting drill)')
        self.g_code.append(f'g0z-{start_depth:.2f}')
        # self.interpolate_hole()
        self.g_code.append(f'g1z-{drill_depth:.2f}f{self.feed_speed:.2f}')
        self.g_code.append(f'g0z-{rapid_depth:.2f}')

    def interpolate_hole(self):  # this is not currently needed, this is to do a helical interpolation to enlarge the hole
        radius = .5
        self.g_code.append('g91')
        self.g_code.append(f'g2x{radius:.2f}z-{radius/2:.2f}r{radius/2:.2f}f15000')
        self.g_code.append(f'g2x-{radius*2:.2f}z-{radius/2:.2f}r{radius:.2f}')
        self.g_code.append(f'g2x{radius*2:.2f}z-{radius/2}r{radius:.2f}')
        self.g_code.append(f'g2x-{radius*2:.2f}z-{radius/2}r{radius:.2f}')
        self.g_code.append(f'g2x{radius * 2:.2f}z-{radius / 2:.2f}r{radius:.2f} ')
        self.g_code.append(f'g2x-{radius:.2f}z-{radius / 2:.2f}r{radius / 2:.2f}')
        self.g_code.append('g90')

    def release_all_clamps(self):
        self.g_code.append('m63(release all clamps)')
        self.g_code.append('m65')
        self.g_code.append('m67')
        self.g_code.append('m69')
        self.g_code.append('m71')
        self.g_code.append('m73')

    def startup(self):
        #y_height = self.y_zero + self.hole_height
        # self.g_code.append(f'g0y-{y_height}z-{self.z_zero}')  # move to starting y, z coordinates
        # self.g_code.append(f'm3s{self.spindle_speed}')  # turn spindle on and set speed
        # self.g_code.append('g4p3')  # delay to allow spindle to start
        #@TODO we have to found alternative for this
        #if self.dowel_on:
        self.g_code.append('m80(start bowl)')  # start vibratory bowl
        pass

    def end_cycle(self):
        # self.g_code.append('m5')
        # self.release_all_clamps()
        self.g_code.append('m81(turn off vibratory bowl)')  # stop vibratory bowl

    def inject_glue(self):
        self.g_code.append('m78(inject glue)')  # turn on water injector
        self.g_code.append(f'g4p{self.injection_time:.2f}(injection time delay)')  # delay for water injection
        self.g_code.append('m79(turn off injector)')  # turn off water injector
        self.g_code.append(f'g4p{self.injection_time * 4:.2f}')

    def insert_dowel(self):
        # self.g_code.append(f'g4p{self.insertion_delay}')  # delay
        self.g_code.append('m74(insert dowel)')  # insert dowel
        self.g_code.append(f'g4p{self.insertion_time:.2f}')  # delay to complete dowel insertion
        self.g_code.append('m75(retract inserter)')  # retract dowel inserter
        # self.g_code.append(f'g4p{self.insertion_delay}')  # delay to complete dowel retraction
        self.g_code.append('m76(release new dowel)')  # release dowel
        self.g_code.append(f'g4p{self.dowel_release_time:.2f}(delay for new dowel)')
        self.g_code.append('m77(close dowel release)')  # release dowel
        self.g_code.append(f'g4p{self.insertion_delay:.2f}')
        self.g_code.append('g91')
        self.g_code.append('g0a15')
        self.g_code.append('g90')

    def left_cut_new(self, width, direction, dowels_profiles):
        target_width = width - self.back_distance
        filtered_profiles = list(filter(lambda profile:profile["distance_from_edge"] <= target_width, dowels_profiles))
        for dowel_profile in filtered_profiles:
            hole_start = dowel_profile["distance_from_edge"]
            hole_height = dowel_profile["distance_from_face"]
            dowel_protrusion = dowel_profile["dowel_protrusion"]
            drill_depth = dowel_profile["drill_depth"]
            target_width = width - self.back_distance
            if direction == 'forward':
                x_left_start = self.left_x_zero + hole_start
            else:
                x_left_start = (self.fence_distance + self.left_x_zero) - width + hole_start
            pos = x_left_start
            y = (self.y_zero - hole_height) + self.y_interpolate(pos)
            print(f'y dim is: {y :.2f}')
            dowel_projection = -1 * (dowel_protrusion - self.dowel_protrusion_zero)

            # print(f'dowel projection: {dowel_projection :.2f}')
            self.g_code.append(f'g0x-{pos:.2f}y-{y:.2f}z-{self.z_zero:.2f}(left dowel position)')
            self.drill_hole(drill_depth)
            if dowel_profile["glue"] or dowel_profile["dowel"]:
                self.g_code.append(
                    f'g0x-{pos + self.drill_insert_offset :.2f}y-{y - self.drill_insert_height_offset:.2f}a-{dowel_projection:.2f}')
                if dowel_profile["glue"]:
                    self.inject_glue()
                if dowel_profile["dowel"]:
                    self.insert_dowel()

    def right_cut_new(self, width, direction, dowels_profiles):
        target_width = width - self.back_distance
        filtered_profiles = list(filter(lambda profile: profile["distance_from_edge"]<= target_width , dowels_profiles))
        filtered_profiles.sort(key=lambda profile:profile["distance_from_edge"] , reverse=True)
        for dowel_profile in filtered_profiles:
            hole_start = dowel_profile["distance_from_edge"]
            hole_height = dowel_profile["distance_from_face"]
            dowel_protrusion = dowel_profile["dowel_protrusion"]
            drill_depth = dowel_profile["drill_depth"]
            target_width = width - self.back_distance
            if direction == 'forward':
                x_right_start = self.fence_distance + self.left_x_zero - hole_start
            else:
                x_right_start = self.left_x_zero + width - hole_start
            pos = x_right_start
            y = (self.y_zero - hole_height) + self.y_interpolate(pos)
            dowel_projection = -1 * (dowel_protrusion - self.dowel_protrusion_zero)
            # print(f'dowel projection: {dowel_projection:.2f}')
            self.g_code.append(f'g0x-{pos:.2f}y-{y:.2f}z-{self.z_zero:.2f}(right dowel position)')
            self.drill_hole(drill_depth)
            if dowel_profile["glue"] or dowel_profile["dowel"]:
                self.g_code.append(
                    f'g0x-{pos + self.drill_insert_offset :.2f}y-{y - self.drill_insert_height_offset :.2f}a-{dowel_projection:.2f}')
                if dowel_profile["glue"]:
                    self.inject_glue()
                if dowel_profile["dowel"]:
                    self.insert_dowel()

    def left_clamp(self, width):
        if width >= 89:
            self.g_code.append('m62(clamp 1)')  # first clamp
        if width >= 292:
            self.g_code.append('m64(clamp 2)')
        if width >= 406:
            self.g_code.append('m66(clamp 3)')
        if width >= 558:
            self.g_code.append('m68(clamp 4)')
        if width >= 673:
            self.g_code.append('m70(clamp 5)')
        if width >= 876:
            self.g_code.append('m72(clamp 6)')

    def release_left_clamp(self, width):
        if width >= 89:
            self.g_code.append('m63(release 1)')  # first clamp
        if width >= 292:
            self.g_code.append('m65(release 2)')
        if width >= 406:
            self.g_code.append('m67(release 3)')
        if width >= 558:
            self.g_code.append('m69(release 4)')
        if width >= 673:
            self.g_code.append('m71(release 5)')
        if width >= 876:
            self.g_code.append('m73(release 6)')

    def right_clamp(self, width):
        if width >= 89:
            self.g_code.append('m72(clamp 6)')  # first clamp
        if width >= 292:
            self.g_code.append('m70(clamp 5)')
        if width >= 406:
            self.g_code.append('m68(clamp 4)')
        if width >= 558:
            self.g_code.append('m66(clamp 3)')
        if width >= 673:
            self.g_code.append('m64(clamp 2)')
        if width >= 876:
            self.g_code.append('m62(clamp 1)')

    def release_right_clamp(self, width):
        if width >= 89:
            self.g_code.append('m73(release 6)')  # first clamp
        if width >= 292:
            self.g_code.append('m71(release 5)')
        if width >= 406:
            self.g_code.append('m69(release 4)')
        if width >= 558:
            self.g_code.append('m67(release 3)')
        if width >= 673:
            self.g_code.append('m65(release 2)')
        if width >= 876:
            self.g_code.append('m63(release 1)')

    def back_reference(self, width, side, dowels_profiles={}):
        print(f'you activated back reference {width} {side}')
        self.startup()
        if side == 'left':
            self.left_clamp(width)
            self.right_cut_new(width, 'reverse', dowels_profiles)
            self.release_left_clamp(width)
        if side == 'right':
            self.right_clamp(width)
            self.left_cut_new(width, 'reverse', dowels_profiles)
            self.release_right_clamp(width)
        self.end_cycle()

        return self.g_code

    def custom_size(self, width, side, dowels_profiles={}):
        # print(f'you activated custom size {width :.2f} {side:.2f}')
        self.startup()
        if side == 'left':
            self.left_clamp(width)
            self.left_cut_new(width, 'forward', dowels_profiles)
        elif side == 'right':
            self.right_clamp(width)
            self.right_cut_new(width, 'forward', dowels_profiles)
        self.end_cycle()

        return self.g_code


def main():
    generate = GenerateCode()  # class instantiated
    f = open('test_g_code.nc', 'w')
    p = input('enter standard or custom: ')
    if p == 's':
        left = float(input('enter the left part width: '))
        right = float(input('enter the right part width: '))
        f.write('\n'.join(map(str, generate.calculate(left, right))))

    elif p == 'c':
        custom_width = float(input('enter part width: '))
        side = str(input('enter side: '))
        f.write('\n'.join(map(str, generate.custom_size(custom_width, side))))
    elif p == 'r':
        width = float(input('enter width: '))
        side = str(input('enter side: '))
        f.write('\n'.join(map(str, generate.back_reference(width, side))))

    f.close()

def main_mo():
    SAMPLE_PROFILE = [
        {
            "distance_from_edge": 10.0,
            "distance_from_face": 11.0,
            "dowel_protrusion": 12.0,
            "drill_depth": 13.0,
            "glue": True,
            "dowel": True
        },
        {
            "distance_from_edge": 11.0,
            "distance_from_face": 11.0,
            "dowel_protrusion": 12.0,
            "drill_depth": 13.0,
            "glue": True,
            "dowel": True
        },
        {
            "distance_from_edge": 12.0,
            "distance_from_face": 11.0,
            "dowel_protrusion": 12.0,
            "drill_depth": 13.0,
            "glue": True,
            "dowel": True
        },
        {
            "distance_from_edge": 12.0,
            "distance_from_face": 11.0,
            "dowel_protrusion": 12.0,
            "drill_depth": 13.0,
            "glue": True,
            "dowel": True
        },
        {
            "distance_from_edge": 15.0,
            "distance_from_face": 11.0,
            "dowel_protrusion": 12.0,
            "drill_depth": 13.0,
            "glue": True,
            "dowel": True
        },
        {
            "distance_from_edge": 15.0,
            "distance_from_face": 11.0,
            "dowel_protrusion": 12.0,
            "drill_depth": 13.0,
            "glue": True,
            "dowel": True
        },
        {
            "distance_from_edge": 13.0,
            "distance_from_face": 11.0,
            "dowel_protrusion": 12.0,
            "drill_depth": 13.0,
            "glue": True,
            "dowel": True
        },
        {
            "distance_from_edge": 12.0,
            "distance_from_face": 11.0,
            "dowel_protrusion": 12.0,
            "drill_depth": 13.0,
            "glue": True,
            "dowel": True
        },
        {
            "distance_from_edge": 10.0,
            "distance_from_face": 11.0,
            "dowel_protrusion": 12.0,
            "drill_depth": 13.0,
            "glue": True,
            "dowel": True
        },
        {
            "distance_from_edge": 10.0,
            "distance_from_face": 11.0,
            "dowel_protrusion": 12.0,
            "drill_depth": 13.0,
            "glue": True,
            "dowel": True
        },
        {
            "distance_from_edge": 10.0,
            "distance_from_face": 11.0,
            "dowel_protrusion": 12.0,
            "drill_depth": 13.0,
            "glue": True,
            "dowel": True
        },
        {
            "distance_from_edge": 10.0,
            "distance_from_face": 11.0,
            "dowel_protrusion": 12.0,
            "drill_depth": 13.0,
            "glue": True,
            "dowel": True
        }
    ]
    generate = GenerateCode()  # class instantiated
    f = open('test_g_code.nc', 'w')
    f.write('\n'.join(map(str, generate.calculate(300, 0, SAMPLE_PROFILE ))))
    f.close()

if __name__ == "__main__":
    main_mo()
