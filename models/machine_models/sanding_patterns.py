import os

try:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    from django.core.wsgi import get_wsgi_application

    application = get_wsgi_application()
except Exception as e:
    print(e)

from models.machine_models.generate_config import feed_speed_max
from apps.sanding_machine import models
from math import ceil
from models.machine_models.sander import SanderControl


class SandingGenerate:
    def __init__(self, pass_: models.SandingProgramPass, door_style: models.DoorStyle, part_length,
                 part_width):

        self.g_code = []
        self.__current_pass = pass_
        self.sander_selection = SanderControl(pass_.sander)
        self._active_sander_id = pass_.sander.pk
        self.part_length = part_length
        self.part_width = part_width
        # self.frame_width = door_style.get_value("outside_edge_width") + \
        #                    door_style.get_value("inside_edge_width") + \
        #                    door_style.get_value("frame_width")
        # self.hold_back = door_style.get_value("hold_back_inside_edge")
        self.frame_add = door_style.get_value("inside_edge_width") + door_style.get_value("hold_back_inside_edge")
        self.pressure = 10 * (self.sander_selection.map_pressure(self.__current_pass.pressure_value))
        # print(f'pressure {self.pressure}')
        # print(f'loaded: {part_type}, {pass_.sander}, {self.part_length}, {self.part_width},'
        #      f' {self.frame_width}, {self.__current_pass.hangover_value}, {self.__current_pass.overlap_value},'
        #      f' {self.__current_pass.speed_value}, {self.hold_back}')

    def slab(self):
        overhang_mm_x = self.__current_pass.hangover_value / 100 * self.sander_selection.get_x_value()
        overhang_mm_y = self.__current_pass.hangover_value / 100 * self.sander_selection.get_y_value()
        offset_x = self.sander_selection.get_x_value() / 2 - overhang_mm_x
        offset_y = self.sander_selection.get_y_value() / 2 - overhang_mm_y
        outside_box = overhang_mm_x + offset_x, overhang_mm_y + offset_y, self.part_length - overhang_mm_x - offset_x, \
                      self.part_width - overhang_mm_y - offset_y
        print(f'Outside box: {outside_box}')
        return outside_box

    def frame(self):
        # todo, look at changing the way we pass the frame info.  likely want to implement new strategy
        effective_sander_width = self.sander_selection.get_y_value() - (
                (self.sander_selection.get_y_value() * (self.__current_pass.hangover_value / 100)) * 2)
        if self.frame_width <= effective_sander_width:
            center_positions = (self.frame_width / 2, self.frame_width / 2), \
                               (self.frame_width / 2, self.part_width - (self.frame_width / 2)), \
                               (self.part_length - (self.frame_width / 2), self.part_width - (self.frame_width / 2)), \
                               (self.part_length - (self.frame_width / 2), self.frame_width / 2)
            print(f'center: {center_positions}')
            self.g_code.append(self.sander_selection.get_offset())
            self.g_code.append(f'f{round(feed_speed_max * int(self.__current_pass.speed_value) / 100, 1)}')
            self.g_code.append(self.sander_selection.get_work_plane())
            self.g_code.append(f'g0x-{center_positions[0][0]}y{center_positions[0][0]}')
            self.g_code.append(self.sander_selection.on(self.pressure))
            self.g_code.append(f'g1y{center_positions[1][1]}')
            self.g_code.append(f'g1x-{center_positions[2][0]}')
            self.g_code.append(f'g1y{center_positions[3][1]}')
            self.g_code.append(f'g1x-{center_positions[0][0]}')
            self.g_code.append(self.sander_selection.off())
            # self.g_code.append('g53g0x0z0')
        else:
            start_positions = (0, 0), (0, self.part_width), (self.part_length, self.part_width), (self.part_length, 0)
            inside_edge = (self.frame_width, self.frame_width), \
                          (self.frame_width, self.part_width - self.frame_width), \
                          (self.part_length - self.frame_width, self.part_width - self.frame_width), \
                          (self.part_length - self.frame_width, self.frame_width)
            overhang_mm_x = self.__current_pass.hangover_value / 100 * self.sander_selection.get_x_value()
            # print(f'overhang x :{overhang_mm_x}')
            overhang_mm_y = self.__current_pass.hangover_value / 100 * self.sander_selection.get_y_value()
            offset_x = self.sander_selection.get_x_value() / 2 - overhang_mm_x
            offset_y = self.sander_selection.get_y_value() / 2 - overhang_mm_y
            print('sand in two passes')
            print(f'starting: {start_positions}')
            print(f'inside: {inside_edge}')
            print(f'offsets: {offset_x}, {offset_y}')
            self.g_code.append(self.sander_selection.get_offset())
            self.g_code.append(f'f{round(feed_speed_max * int(self.__current_pass.speed_value) / 100, 1)}')
            self.g_code.append(self.sander_selection.get_work_plane())
            self.g_code.append(f'g0x-{start_positions[0][0] + offset_x}z{start_positions[0][1] + offset_y}')
            self.g_code.append(self.sander_selection.on(self.pressure))
            self.g_code.append(f'g1z{start_positions[1][1] - offset_y}')
            self.g_code.append(f'g1x-{start_positions[2][0] - offset_x}')
            self.g_code.append(f'g1z{start_positions[3][1] + offset_y}')
            self.g_code.append(f'g1x-{start_positions[0][0] + offset_x}')
            self.g_code.append(f'g1x-{inside_edge[0][0] - offset_x}z{inside_edge[0][1] - offset_y}')
            self.g_code.append(f'g1z{inside_edge[1][1] + offset_y}')
            self.g_code.append(f'g1x-{inside_edge[2][0] + offset_x}')
            self.g_code.append(f'g1z{inside_edge[3][1] - offset_y}')
            self.g_code.append(f'g1x-{inside_edge[0][0] - offset_x}')
            self.g_code.append(self.sander_selection.off())

        return self.g_code

    def panel_spiral_in(self, outside_box, perimeter, entire_panel=True, panel_offset=float):
        panel_offset = panel_offset * 25.4
        print(f'panel offset: {panel_offset}')
        if outside_box[2] >= outside_box[3]:

            y_half_width = ((outside_box[3] - outside_box[1]) / 2) + panel_offset  # need to offset for center of panel
            print(self.sander_selection.get_y_value())
            passes = ceil(y_half_width / (
                    (1 - float(self.__current_pass.overlap_value / 100)) * self.sander_selection.get_y_value()))
            print(f'x is longer than y, y half width : {y_half_width}, passes: {passes}')
            step_over_y = y_half_width / passes
            step_over_x = (self.sander_selection.get_x_value() * (1 - float(self.__current_pass.overlap_value / 100)))
        else:
            x_half_width = (outside_box[2] - outside_box[0]) / 2
            print(f'y is longer than x, x half width: {x_half_width}')
            # todo need to develop this logic

        self.g_code.append(self.sander_selection.get_offset())
        self.g_code.append(f'f{round(feed_speed_max * int(self.__current_pass.speed_value) / 100, 1)}')
        self.g_code.append(self.sander_selection.get_work_plane())
        # ramp in start, not currently ramping, but may not be necessary
        self.g_code.append(
            f'g0x-{round(outside_box[0] + (step_over_x * 2), 1)}y{round(outside_box[3] - (step_over_y / 2), 1)}')  # still working on this

        self.g_code.append(self.sander_selection.on(self.pressure))

        self.g_code.append(f'g1x-{round(outside_box[0], 1)}y{round(outside_box[3], 1)}(start)')  # start of box
        self.g_code.append(f'g1y{round(outside_box[1], 1)}(1)')
        self.g_code.append(f'g1x-{round(outside_box[2], 1)}(2)')
        self.g_code.append(f'g1y{round(outside_box[3], 1)}(3)')
        self.g_code.append(f'g1x-{round(outside_box[0], 1)}(end of perimeter)')

        if perimeter:
            # start at far side on y
            self.g_code.append(
                f'g1x-{round(outside_box[0], 1)}y{round(outside_box[3], 1)}(extra perimeter)')  # start of box
            self.g_code.append(f'g1y{round(outside_box[1], 1)}(1)')
            self.g_code.append(f'g1x-{round(outside_box[2], 1)}(2)')
            self.g_code.append(f'g1y{round(outside_box[3], 1)}(3)')
            self.g_code.append(f'g1x-{round(outside_box[0], 1)}(end of perimeter)')

        if entire_panel:
            self.g_code.append(
                f'g1x-{round(outside_box[0] + step_over_x, 1)}y{round(outside_box[3] - step_over_y, 1)}(before entering for loop)')

            for i in range(passes):
                self.g_code.append(f'g1x-{round(outside_box[2] - (step_over_x * (i + 1)))}(1-{i + 1})')
                y_2_pass = round(outside_box[1] + (step_over_y * (i + 1)))
                self.g_code.append(f'g1y{y_2_pass}(2-{i + 1})')
                self.g_code.append(f'g1x-{round(outside_box[0] + step_over_x * (i + 1))}(3-{i + 1})')
                self.g_code.append(f'g1y{round(outside_box[3] - (step_over_y * (i + 2)), 1)}(4-{i + 1})')
                if y_2_pass >= y_half_width:
                    break
            self.g_code.append(f'g1x-{outside_box[2] - step_over_x}(end)')

            self.g_code.append(self.sander_selection.off())

        return self.g_code

    def panel_parallel_x(self):
        """
        method to sand panels and slabs parallel on x
        """

    def panel_parallel_y(self):
        """
        method to sand panels and slabs parallel on y
        """

    def panel(self, panel_operation):
        print(f'panel operation: {panel_operation}')
        panel_x_dim = round(panel_operation[0] * 25.4, 1)
        panel_y_dim = round(panel_operation[1] * 25.4, 1)
        xpos = round(panel_operation[2] * 25.4, 1)
        ypos = round(panel_operation[3] * 25.4, 1)
        print(f'x: {panel_x_dim}, y: {panel_y_dim}, xpos: {xpos}, ypos: {ypos}')

        if self.sander_selection.get_y_value() >= (panel_y_dim + (self.frame_add * 2)):
            print('sander too wide')
            return None
        elif self.sander_selection.get_x_value() >= (panel_x_dim + (self.frame_add * 2)):
            print('sander too long')
            return None
        starting_boundary = xpos, ypos, panel_x_dim + xpos, panel_y_dim + ypos
        print(f'starting boundary: {starting_boundary}')
        offset_x = self.sander_selection.get_x_value() / 2 + self.frame_add
        offset_y = self.sander_selection.get_y_value() / 2 + self.frame_add
        outside_box = starting_boundary[0] + offset_x, starting_boundary[1] + offset_y, starting_boundary[2] - offset_x, \
                      starting_boundary[3] - offset_y
        print(f'Outside box: {outside_box}')
        return outside_box
