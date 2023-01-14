import cv2
import numpy as np
from typing import List, Tuple, Dict, Any
from models.access_db_parser import Part

"""
created by: jeremiah lemon 1-14-2023
replaces creating part information in draw_utils, along with scaling

class to get all the needed part info from the .tld file.
as we move to cv part identification, this will be replaced.
returns: part dimension, route paths
"""
class getParts:

    def __init__(self) -> None:
        pass


    def create_part_info(parts: List[Part], self):
        
        for part in parts:
            part_height, part_width = part.get_outer_dims()
            rotate_part = False
            if part_height > part_width: # rotating parts to orient to machine correctly
                rotate_part = True
            if rotate_part:
                part_y_dim, part_x_dim = part_width, part_height
            else:
                part_x_dim, part_y_dim = part_width, part_height
            # these are what we need to pass to sander_generate as part size part_length = CustomMachineParamManager.get_value("left_part_length")
            # part_width = CustomMachineParamManager.get_value("left_part_width")
            print(f'part x: {part_x_dim}, y:{part_y_dim}')
            """
            we are not handling shaped parts right now

            if part.shaped:
                outlines = part.get_outlines()
                for pt1, pt2 in outlines:
                    pt1 = (scale_dim_to_pixels(image_width_pixels, real_width_in, pt1[0]),
                        scale_dim_to_pixels(image_height_pixels, real_height_in, pt1[1]))
                    pt2 = (scale_dim_to_pixels(image_width_pixels, real_width_in, pt2[0]),
                        scale_dim_to_pixels(image_height_pixels, real_height_in, pt2[1]))
                    cv2.line(image, pt1, pt2, (0, 255, 0), 3)
            
            """
            # now we have to draw the operations of the part on the image

            panel_no = 0
            self.panel_info = []
            # todo, add here whether part contains operations, save to CustomMachineParamManager.get_value('left_slab_selected')
            for operation in part.operations:
                if operation.tool_id == 107:
                    continue
                op_height, op_width = operation.get_outer_dims()
                if rotate_part:
                    panel_y_dim, panel_x_dim = op_width, op_height
                else:
                    panel_x_dim, panel_y_dim = op_width, op_height
                
                xpos, ypos = operation.get_init_pos()
                if rotate_part:
                    xpos, ypos = ypos, xpos
                    
                panel_x_dim = op_width
                panel_y_dim = op_height
                print(f'panel #{panel_no}, x: {panel_x_dim}, y: {panel_y_dim}')
                # todo these are what we need to pass to sanding generate, currently sending list?
                panel_no += 1
                
                """
                we are not currently handling outlines, these are for
                operations that are not rectangles
                outlines = operation.get_outlines()

                """
                self.panel_info.append = (panel_x_dim, panel_y_dim, xpos, ypos, operation.tool_id)

        # not sure if we want to return in this format, we may want to save to internal db
        return [(part_x_dim, part_y_dim), self.panel_info] # need to return for each operation


if __name__ == "__main__":
    pass
