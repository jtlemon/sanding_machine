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


class GenerateCode:
    def __init__(self, joint_profile, bit_profile):
        # general settings
        self.on_center_spacing = self.config.getfloat('general settings', 'onCenterSpacing')
        self.inner_radius = self.config.getfloat('general settings', 'innerRadius')
        self.outer_radius = self.config.getfloat('general settings', 'outerRadius')
        self.feed_speed = self.config.getfloat('general settings', 'feedspeed')
        self.spindle_speed = self.config.getfloat('general settings', 'spindlespeed')
        # active side
        self.left_active = self.config.getfloat('active side', 'leftactive')
        self.right_active = self.config.getfloat('active side', 'rightactive')
        # left settings
        self.left_depth = self.config.getfloat('left settings', 'leftdepth')
        self.left_width = self.config.getfloat('left settings', 'leftwidth')
        self.left_height = self.config.getfloat('left settings', 'leftheight')
        # self.left_height_abs = self.config.getfloat('left settings', 'leftheightabs')
        self.left_zero = self.config.getfloat('left settings', 'leftzero')
        self.left_y_zero = self.config.getfloat('left settings', 'leftyzero')
        self.left_upper_fence = self.config.getfloat('left settings', 'upper fence')
        # right settings
        self.right_depth = self.config.getfloat('right settings', 'rightdepth')
        self.right_width = self.config.getfloat('right settings', 'rightwidth')
        self.right_height = self.config.getfloat('right settings', 'rightheight')
        # self.right_height_abs = self.config.getfloat('right settings', 'rightheightabs')
        self.right_zero = self.config.getfloat('right settings', 'rightzero')
        self.right_y_zero = self.config.getfloat('right settings', 'rightyzero')
        self.right_upper_fence = self.config.getfloat('right settings', 'upper fence')

        self.g_code = []

    def calculate(self):
        left_part_width = self.left_active * 25.4  # convert left active dim to metric
        right_part_width = self.right_active * 25.4  # convert right active dim to metric
        # score cut- need to generate score cut code
        left_inner_radius = (self.left_width / 2)
        right_inner_radius = self.right_width / 2
        left_outer_radius = ((self.on_center_spacing - self.left_width) / 2)
        right_outer_radius = (self.on_center_spacing - self.right_width) / 2
        self.g_code.append(f'f{self.feed_speed*25.4}')
        self.g_code.append(f'm3s{self.spindle_speed}')
        self.g_code.append('g4p4')

        # left cut
        if self.left_active != 0:
            number_of_cuts = (math.ceil(left_part_width / self.on_center_spacing)) + 1
            score_cut_start = (number_of_cuts * self.on_center_spacing) + self.left_zero
            score_cut_depth = self.left_y_zero - left_outer_radius
            self.g_code.append(f'g0z-{self.left_height}')
            self.g_code.append(f'g0x-{score_cut_start}y-{score_cut_depth}')
            self.g_code.append(f'g1x-{self.left_zero}')  # move to starting position of left piece
            self.g_code.append(f'g0y-{self.left_y_zero}')
            self.g_code.append('g91')  # change to incremental units
            for i in range(number_of_cuts):
                self.g_code.append(f'g01y-{self.left_depth}')  # plunge in to piece
                self.g_code.append(f'g02x-{left_inner_radius}y-{left_inner_radius}r{left_inner_radius}')  # arc 1
                # self.g_code.append(f'g01x-{socket_straight}')  # move over inside socket
                self.g_code.append(
                    f'g02x-{left_inner_radius}y{left_inner_radius}r{left_inner_radius}')  # arc 2 in socket
                self.g_code.append(f'g01y{self.left_depth}')  # retract out of socket
                self.g_code.append(f'g03x-{left_outer_radius}y{left_outer_radius}r{left_outer_radius}')  # arc 1 outer
                # self.g_code.append(f'g01x-{step_over_straight}')
                self.g_code.append(
                   f'g03x-{left_outer_radius}y-{left_outer_radius}r{left_outer_radius}')  # arc 2 outer
            self.g_code.append(f'g01y-{self.left_depth}')
            self.g_code.append('g90')  # change to absolute units
            self.g_code.append('g0y0')

        # right cut
        if self.right_active != 0:

            number_of_cuts = (math.ceil(right_part_width / self.on_center_spacing))+1
            right_score_cut_end = self.right_zero - (self.on_center_spacing * number_of_cuts)
            right_score_cut_depth = self.right_y_zero - right_outer_radius
            self.g_code.append(f'g0z-{self.right_height}')
            self.g_code.append(f'g0x-{self.right_zero}y-{right_score_cut_depth}')
            self.g_code.append(f'g1x-{right_score_cut_end}')  # move to starting position of left piece
            # self.g_code.append(f'g0y-{self.left_y_zero}')
            print(f'number of cuts {number_of_cuts}')
            right_starting = self.right_zero - (self.on_center_spacing * number_of_cuts)
            print(f'right starting {right_starting}')
            self.g_code.append(f'g0x-{right_starting}')
            self.g_code.append(f'g0y-{self.right_y_zero}')
            self.g_code.append('g91')
            for i in range(number_of_cuts):
                self.g_code.append(f'g01y-{self.right_depth}')
                self.g_code.append(f'g02x-{right_inner_radius}y-{right_inner_radius}r{right_inner_radius}')
                # self.g_code.append(f'g01x-{socket_straight}')
                self.g_code.append(f'g02x-{right_inner_radius}y{right_inner_radius}r{right_inner_radius}')
                self.g_code.append(f'g01y{self.right_depth}')
                self.g_code.append(f'g03x-{right_outer_radius}y{right_outer_radius}r{right_outer_radius}')
                # self.g_code.append(f'g01x-{step_over_straight}')
                self.g_code.append(f'g03x-{right_outer_radius}y-{right_outer_radius}r{right_outer_radius}')
            self.g_code.append(f'g01y-{self.right_depth}')
            self.g_code.append('g90')
            self.g_code.append('g0y0')

        self.g_code.append('g90')
        self.g_code.append('g0y0')
        self.g_code.append('m5')
        self.g_code.append('g0z0')
        self.g_code.append('m68')
        self.g_code.append('g4p.2')
        self.g_code.append('m63')
        self.g_code.append('m67')
        self.g_code.append('m71')
        self.g_code.append('m73')
        self.g_code.append('m65')
        self.g_code.append('g0x-250')
        return self.g_code