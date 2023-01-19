import cv2
import numpy as np
from typing import List, Tuple, Dict, Any
from models.access_db_parser import Part

import open3d as o3d
from scipy.spatial.transform import Rotation as R

"""
created by: jeremiah lemon 1-14-2023
replaces creating part information in draw_utils, along with scaling

class to get all the needed part info from the .tld file.
as we move to cv part identification, this will be replaced.
returns: part dimension, route paths
"""
def return_transformed_pointcloud(part_origin_pcd:o3d.geometry.PointCloud, rotation:List[float], translate:List[float] ):
    transform = np.eye(4)
    translation = np.eye(4)
    r = R.from_euler('ZYX', rotation, degrees=True)
    rotm = r.as_matrix()
    transform[0:3,0:3] = rotm
    translation[0:3,3] = translate
    part_origin_pcd.transform(transform)
    part_origin_pcd.transform(translation)
    part_origin_points = np.insert(np.asarray(part_origin_pcd.points), 3, values=1, axis=1)
    return part_origin_pcd

class getParts:

    def create_part_info(self, parts: List[Part]):
        
        for part in parts:
            part_height, part_width = part.get_outer_dims()
            self.rotate_part = False
            if part_height > part_width: # rotating parts to orient to machine correctly
                self.rotate_part = True
            if self.rotate_part:
                part_y_dim, part_x_dim = part_width, part_height
            else:
                part_x_dim, part_y_dim = part_width, part_height
            # these are what we need to pass to sander_generate as part size part_length = CustomMachineParamManager.get_value("left_part_length")
            # part_width = CustomMachineParamManager.get_value("left_part_width")
            # print(f'part x: {part_x_dim}, y:{part_y_dim}')
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
                elif operation.tool_id == 90:
                    continue
                op_height, op_width = operation.get_outer_dims()
                if self.rotate_part:
                    panel_y_dim, panel_x_dim = op_width, op_height
                else:
                    panel_x_dim, panel_y_dim = op_width, op_height
                
                xpos, ypos = operation.get_init_pos()
                if self.rotate_part:
                    xpos, ypos = ypos, xpos
                
                # print(f'panel #{panel_no}, x: {panel_x_dim}, y: {panel_y_dim}')
                # todo these are what we need to pass to sanding generate, currently sending list?
                panel_no += 1
                
                """
                we are not currently handling outlines, these are for
                operations that are not rectangles
                outlines = operation.get_outlines()

                """
                self.panel_info.append((panel_x_dim, panel_y_dim, xpos, ypos, operation.tool_id))

        # not sure if we want to return in this format, we may want to save to internal db
        return [(part_x_dim, part_y_dim), self.panel_info] # need to return for each operation

    def create_current_part_info(self, parts: List[Part],part_position_id):
        returning_list = []
        current_panel_info = []
        part_info = self.create_part_info(parts)
        
        part_breath = part_info[0][0]
        print(f'part breath: {part_info[0][0]}')
        part_length = part_info[0][1]
        
        # number_of_panel = part_info[1]

        part_height = 0.75 

        if part_position_id == 2 or part_position_id == 1:
            part_x_dim = part_info[0][1]
            print(f'part breath: {part_info[0][0]}')
            part_y_dim = part_info[0][0]        
        else:
            part_x_dim = part_info[0][0]
            print(f'part breath: {part_info[0][0]}')
            part_y_dim = part_info[0][1]
        
        returning_list.append((part_x_dim,part_y_dim))
        # number_of_panel = part_info[1]

        if part_position_id != 4:    
            for panel in part_info[1]:
                panel_breath = panel[0] 
                panel_length = panel[1] 
                panel_x = panel[2] 
                panel_y = panel[3] 


                if part_position_id == 2 or part_position_id == 1:
                    panel_x_dim = panel[1]
                    panel_y_dim = panel[0]    
                else:
                    panel_x_dim = panel[0]
                    panel_y_dim = panel[1]

                
                panel_origin_points = [[panel_x, panel_y, part_height, 1],
                                    [panel_x+panel_breath ,panel_y, part_height, 1],
                                        [panel_x+panel_breath , panel_y+panel_length , part_height, 1],
                                    [panel_x, panel_y+panel_length , part_height, 1]]
                panel_origin_pcd = o3d.geometry.PointCloud()
                panel_origin_pcd.points = o3d.utility.Vector3dVector(np.array(panel_origin_points)[:,0:3])

                if part_position_id == 0: #normal
                    panel_origin_pcd = return_transformed_pointcloud(panel_origin_pcd,[0,0,0],[0,0,0])

                elif part_position_id == 1: #+90
                    panel_origin_pcd = return_transformed_pointcloud(panel_origin_pcd,[90,0,0],[part_length,0,0])

                elif part_position_id == 2: #-90
                    panel_origin_pcd = return_transformed_pointcloud(panel_origin_pcd,[-90,0,0],[0,part_breath,0])

                elif part_position_id == 3: #180
                    panel_origin_pcd = return_transformed_pointcloud(panel_origin_pcd,[180,0,0],[part_breath,part_length,0])
                
                elif part_position_id == 4: #flipped:
                    panel_origin_pcd = return_transformed_pointcloud(panel_origin_pcd,[0,180,0],[part_breath,0,part_height])
                
                elif part_position_id == 5: #mirrored:
                    transform = np.eye(4)
                    translation = np.eye(4)
                    rotm = np.eye(3)
                    rotm[0][0] = -1
                    transform[0:3,0:3] = rotm
                    translation[0:3,3] = [part_breath,0,0]
                    panel_origin_pcd.transform(transform)
                    panel_origin_pcd.transform(translation)
                    # panel_origin_points = np.insert(np.asarray(panel_origin_pcd.points), 3, values=1, axis=1)
                
                pcd_tree = o3d.geometry.KDTreeFlann(panel_origin_pcd)
                [k, idx, _] = pcd_tree.search_knn_vector_3d(np.array([0,0,0]), 1)
                origin_point = np.asarray(panel_origin_pcd.points[idx[0]])

                current_panel_info.append([panel_x_dim,panel_y_dim,origin_point[0],origin_point[1],panel[4]])
            returning_list.append(current_panel_info)
        else:
            returning_list.append(current_panel_info)
        return returning_list
    





if __name__ == "__main__":
    pass
