import cv2
import numpy as np
from typing import List, Tuple, Dict, Any
from models.access_db_parser import Part
from models.get_part_from_tld import getParts
import json
import open3d as o3d
from scipy.spatial.transform import Rotation as R

"""
we probably need to update this.  draw_utils is actually figuring out the part size and panels,
we should create that info in a different class and pass the object to the draw_utils.

"""
def project_3d_to_image(point, mat, dist):
    x_dash = point[0] / point[2]
    y_dash = point[1] / point[2]

    r_2 = x_dash * x_dash + y_dash * y_dash

    x_term1 = x_dash * (1 + dist[0] * r_2 + dist[1] * r_2 * r_2 + dist[4] * r_2 * r_2 * r_2)
    x_term2 = 2 * dist[2] * x_dash * y_dash
    x_term3 = dist[3] * (r_2 + 2 * x_dash * x_dash)

    y_term1 = y_dash * (1 + dist[0] * r_2 + dist[1] * r_2 * r_2 + dist[4] * r_2 * r_2 * r_2)
    y_term3 = 2 * dist[3] * x_dash * y_dash
    y_term2 = dist[2] * (r_2 + 2 * y_dash * y_dash)

    x_ddash = x_term1 + x_term2 + x_term3
    y_ddash = y_term1 + y_term2 + y_term3

    u1 = (mat[0][0] * x_ddash) + mat[0][2]
    v1 = (mat[1][1] * y_ddash) + mat[1][2]

    return u1, v1


class TransformationHandler:
    def __init__(self):
        self.transformation_dict = {}

    def get_aruco_ids(self,image: np.ndarray):
        pass
    def get_transformation(self,id: int):
        pass


def draw_parts_on_image(image: np.ndarray, parts: List[Part], part_position_id:int = 0, work_zone:str = 'left'):
    def scale_dim_to_pixels(real_in_pixels: int, real_in_inches: float, current_in_inches: float) -> int:
        return int(real_in_pixels * (current_in_inches / real_in_inches))

    def return_transformed_points(part_origin_pcd:o3d.geometry.PointCloud, rotation:List[float], translate:List[float] ):
        transform = np.eye(4)
        translation = np.eye(4)
        r = R.from_euler('ZYX', rotation, degrees=True)
        rotm = r.as_matrix()
        transform[0:3,0:3] = rotm
        translation[0:3,3] = translate
        part_origin_pcd.transform(transform)
        part_origin_pcd.transform(translation)
        part_origin_points = np.insert(np.asarray(part_origin_pcd.points), 3, values=1, axis=1)
        return part_origin_points

    def send_points_to_right_work_zone(points, part_breath, machine_x_max_lim = 70*25.4):
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(np.array(points)[:,0:3])
        translation = np.eye(4)
        translation[0:3,3] = [machine_x_max_lim-part_breath,0,0]
        pcd.transform(translation)
        points = np.insert(np.asarray(pcd.points), 3, values=1, axis=1)
        return points

    def drawline(img,pt1,pt2,color,thickness=1,style='dotted',gap=20):
        dist =((pt1[0]-pt2[0])**2+(pt1[1]-pt2[1])**2)**.5
        pts= []
        for i in  np.arange(0,dist,gap):
            r=i/dist
            x=int((pt1[0]*(1-r)+pt2[0]*r)+.5)
            y=int((pt1[1]*(1-r)+pt2[1]*r)+.5)
            p = (x,y)
            pts.append(p)

        if style=='dotted':
            for p in pts:
                cv2.circle(img,p,thickness,color,-1)
        else:
            s=pts[0]
            e=pts[0]
            i=0
            for p in pts:
                s=e
                e=p
                if i%2==1:
                    cv2.line(img,s,e,color,thickness)
                i+=1

    def drawpoly(img,pts,color,thickness=1,style='dotted',):
        s=pts[0]
        e=pts[0]
        pts.append(pts.pop(0))
        for p in pts:
            s=e
            e=p
            drawline(img,s,e,color,thickness,style)


    mtx_json = open('/home/sanding/dovetail_drill_dowel/configurations/custom_configurations/camera_matrix.json')
    # returns JSON object as
    # a dictionary
    data = json.load(mtx_json)
    mtx = np.array([[data['fx'], 0, data['cx']], [0, data['fy'], data['cy']], [0, 0, 1]])
    mtx_json.close()
    dist_json = open('/home/sanding/dovetail_drill_dowel/configurations/custom_configurations/camera_dist.json')
    # returns JSON object as
    # a dictionary
    data = json.load(dist_json)
    dist = np.array([[data["k1"], data["k2"], data["p1"], data["p2"], data["k3"]]])
    dist_json.close()

    part_getter = getParts()
    part_info = part_getter.create_part_info(parts)
    print(f'part info: {part_info}')
    part_breath = part_info[0][0]* 25.4
    print(f'part breath: {part_info[0][0]}')
    part_length = part_info[0][1]* 25.4
    
    # number_of_panel = part_info[1]

    part_height = 0.75 * 25.4
    # cTcnc = np.array([[ 9.99661735e-01,  5.75641957e-03,  2.53629384e-02, -8.61079574e+02],
    # [ 2.00750775e-03, -9.89367360e-01 , 1.45424197e-01 , 4.48560712e+02],
    # [ 2.59303861e-02, -1.45324089e-01, -9.89044248e-01 , 7.28219983e+03],
    # [ 0.00000000e+00,  0.00000000e+00 , 0.00000000e+00,  1.00000000e+00]])

    cTcnc_json = open('/home/sanding/dovetail_drill_dowel/configurations/custom_configurations/cTcnc.json')
    # returns JSON object as
    # a dictionary
    data = json.load(cTcnc_json)
    cTcnc = np.array([[ data['0,0'],  data['0,1'],  data['0,2'],  data['0,3']],
    [ data['1,0'],  data['1,1'],  data['1,2'],  data['1,3']],
    [ data['2,0'],  data['2,1'],  data['2,2'],  data['2,3']],
    [ data['3,0'],  data['3,1'],  data['3,2'],  data['3,3']]])

    
    part_origin_points = [[0, 0, part_height, 1], [part_breath , 0, part_height, 1],
                          [part_breath , part_length , part_height, 1], [0, part_length , part_height, 1]]

    part_origin_pcd = o3d.geometry.PointCloud()
    part_origin_pcd.points = o3d.utility.Vector3dVector(np.array(part_origin_points)[:,0:3])

    # part_position = "flipped"
    '''
    part_position ids
    normal = 0
    rotated plus 90 = 1
    rotated minus 90 = 2
    rotated 180 = 3 
    flipped = 4
    mirrored = 5
    '''


    # work_zone = 'right'

    if part_position_id == 0: #normal
        part_origin_points = return_transformed_points(part_origin_pcd,[0,0,0],[0,0,0])

    elif part_position_id == 1: #+90
        part_origin_points = return_transformed_points(part_origin_pcd,[90,0,0],[part_length,0,0])

    elif part_position_id == 2: #-90
        part_origin_points = return_transformed_points(part_origin_pcd,[-90,0,0],[0,part_breath,0])

    elif part_position_id == 3: #180
        part_origin_points = return_transformed_points(part_origin_pcd,[180,0,0],[part_breath,part_length,0])

    elif part_position_id == 4: #flipped
        part_origin_points = return_transformed_points(part_origin_pcd,[0,180,0],[part_breath,0,part_height])

    elif part_position_id == 5: #mirrored
        transform = np.eye(4)
        translation = np.eye(4)
        rotm = np.eye(3)
        rotm[0][0] = -1
        transform[0:3,0:3] = rotm
        translation[0:3,3] = [part_breath,0,0]
        part_origin_pcd.transform(transform)
        part_origin_pcd.transform(translation)
        part_origin_points = np.insert(np.asarray(part_origin_pcd.points), 3, values=1, axis=1)

    if work_zone == 'right' and part_position_id != 1 and part_position_id != 2:
        part_origin_points = send_points_to_right_work_zone(part_origin_points,part_breath)
    elif work_zone == 'right' and (part_position_id == 1 or part_position_id == 2):
        part_origin_points = send_points_to_right_work_zone(part_origin_points,part_length)
    part_pixel_points = []

    for point in part_origin_points:
        part_camera_point = cTcnc @ point
        u, v = project_3d_to_image(part_camera_point[0:3], mtx, dist[0])
        print('uv:', u,v)
        part_pixel_points.append([int(u), int(v)])
    center = (int(part_pixel_points[0][0]+(part_pixel_points[0][0]-part_pixel_points[3][0])),
              int(part_pixel_points[0][1]-(part_pixel_points[0][1]-part_pixel_points[3][1])/2))
    cv2.putText(image, str(part_info[0][1]), (center[0],center[1] ), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)
    center = (int(part_pixel_points[0][0]+(part_pixel_points[1][0]-part_pixel_points[0][0])/2),
              int(part_pixel_points[0][1]-(part_pixel_points[1][1]-part_pixel_points[0][1])))
 
    cv2.putText(image, str(part_info[0][0]), (center[0],center[1] ), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)

    pts = np.array(part_pixel_points,
                   np.int32)

    pts = pts.reshape((-1, 1, 2))               
    # Blue color in BGR
    color = (255, 0, 0)

    # Line thickness of 2 px
    thickness = 7

    # Using cv2.polylines() method
    # Draw a Blue polygon with 
    # thickness of 1 px
    if part_position_id == 4: # "flipped"
        # image = cv2.polylines(image, [pts], True, color, thickness,cv2.LINE_8)
        # todo, we only want the panel to be dotted, not the outline
        drawpoly(image,part_pixel_points,color,thickness,style='dotted',)

    else:
        image = cv2.polylines(image, [pts], True, color, thickness)

    for panel in part_info[1]:
        panel_breath = panel[0] * 25.4
        panel_length = panel[1] * 25.4
        panel_x = panel[2] * 25.4
        panel_y = panel[3] * 25.4
        
        panel_origin_points = [[panel_x, panel_y, part_height, 1],
                               [panel_x+panel_breath ,panel_y, part_height, 1],
                                [panel_x+panel_breath , panel_y+panel_length , part_height, 1],
                               [panel_x, panel_y+panel_length , part_height, 1]]

        panel_origin_pcd = o3d.geometry.PointCloud()
        panel_origin_pcd.points = o3d.utility.Vector3dVector(np.array(panel_origin_points)[:,0:3])

        # part_position = "rotated_180"

        if part_position_id == 0: #normal
            panel_origin_points = return_transformed_points(panel_origin_pcd,[0,0,0],[0,0,0])

        elif part_position_id == 1: #+90
            panel_origin_points = return_transformed_points(panel_origin_pcd,[90,0,0],[part_length,0,0])

        elif part_position_id == 2: #-90
            panel_origin_points = return_transformed_points(panel_origin_pcd,[-90,0,0],[0,part_breath,0])

        elif part_position_id == 3: #180
            panel_origin_points = return_transformed_points(panel_origin_pcd,[180,0,0],[part_breath,part_length,0])
        
        elif part_position_id == 4: #flipped:
            panel_origin_points = return_transformed_points(panel_origin_pcd,[0,180,0],[part_breath,0,part_height])
        
        elif part_position_id == 5: #mirrored:
            transform = np.eye(4)
            translation = np.eye(4)
            rotm = np.eye(3)
            rotm[0][0] = -1
            transform[0:3,0:3] = rotm
            translation[0:3,3] = [part_breath,0,0]
            panel_origin_pcd.transform(transform)
            panel_origin_pcd.transform(translation)
            panel_origin_points = np.insert(np.asarray(panel_origin_pcd.points), 3, values=1, axis=1)


        if work_zone == 'right'and part_position_id != 1 and part_position_id != 2:
            panel_origin_points = send_points_to_right_work_zone(panel_origin_points,part_breath)
        elif work_zone == 'right' and (part_position_id == 1 or part_position_id == 2):
            panel_origin_points = send_points_to_right_work_zone(panel_origin_points,part_length)

        panel_pixel_points = []

        for point in panel_origin_points:
            panel_camera_point = cTcnc @ point
            u, v = project_3d_to_image(panel_camera_point[0:3], mtx, dist[0])
            panel_pixel_points.append([int(u), int(v)])

        pts = np.array(panel_pixel_points,
                       np.int32).reshape((-1, 1, 2))
        pts = pts.reshape((-1, 1, 2))
        color = (0, 0, 255)

        if part_position_id == 4: #"flipped"
            # image = cv2.polylines(image, [pts], True, color, thickness,cv2.LINE_8)
            drawpoly(image,panel_pixel_points,color,thickness,style='dotted',)
        else:
            image = cv2.polylines(image, [pts], True, color, thickness)


    # image_height_pixels, image_width_pixels = image.shape[:2]
    # # now we need to scale the dimensions of the part to the image
    # real_height_in, real_width_in = 36, 72  # in inches
    # for part in parts:
    #     part_height, part_width = part.get_outer_dims()
    #     rotate_part = False
    #     if part_height > part_width: # rotating parts to orient to machine correctly
    #         rotate_part = True
    #     if rotate_part:
    #         part_height, part_width = part_width, part_height
    #     part_x_dim = part_width
    #     part_y_dim = part_height
    #     # these are what we need to pass to sander_generate as part size part_length = CustomMachineParamManager.get_value("left_part_length")
    #     # part_width = CustomMachineParamManager.get_value("left_part_width")
    #     print(f'part x: {part_x_dim}, y:{part_y_dim}')
    #     part_height_pixels = scale_dim_to_pixels(image_height_pixels, real_height_in, part_height)
    #     part_width_pixels = scale_dim_to_pixels(image_width_pixels, real_width_in, part_width)
    #     # now we have to draw a rectangle that represents the part on the image
    #
    #     cv2.rectangle(image, (0, 0), (part_width_pixels, part_height_pixels), (0, 255, 0), 4)
    #     cv2.putText(image, str(part_height), (part_width_pixels, part_height_pixels // 2 - 35), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)
    #     # M = cv2.getRotationMatrix2D((part_width_pixels, part_height_pixels), 90, 1)
    #     # image = cv2.warpAffine(image, M, (image.shape[1], image.shape[0]))
    #     cv2.putText(image, str(part_width), (part_height_pixels // 2 -150 , part_height_pixels + 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    #     # now we have to draw the outlines of the part on the image
    #     if part.shaped:
    #         outlines = part.get_outlines()
    #         for pt1, pt2 in outlines:
    #             pt1 = (scale_dim_to_pixels(image_width_pixels, real_width_in, pt1[0]),
    #                    scale_dim_to_pixels(image_height_pixels, real_height_in, pt1[1]))
    #             pt2 = (scale_dim_to_pixels(image_width_pixels, real_width_in, pt2[0]),
    #                    scale_dim_to_pixels(image_height_pixels, real_height_in, pt2[1]))
    #             cv2.line(image, pt1, pt2, (0, 255, 0), 3)
    #     # now we have to draw the operations of the part on the image
    #     panel_no = 0
    #     # todo, add here whether part contains operations, save to CustomMachineParamManager.get_value('left_slab_selected')
    #     for operation in part.operations:
    #         if operation.tool_id == 107:
    #             continue
    #         op_height, op_width = operation.get_outer_dims()
    #         if rotate_part:
    #             op_height, op_width = op_width, op_height
    #         op_height_pixels = scale_dim_to_pixels(image_height_pixels, real_height_in, op_height)
    #         op_width_pixels = scale_dim_to_pixels(image_width_pixels, real_width_in, op_width)
    #         # now we have to draw a rectangle that represents the operation on the image
    #         xpos, ypos = operation.get_init_pos()
    #         if rotate_part:
    #             xpos, ypos = ypos, xpos
    #         # print(xpos, ypos )
    #         panel_x_dim = op_width
    #         panel_y_dim = op_height
    #         print(f'panel #{panel_no}, x: {panel_x_dim}, y: {panel_y_dim}')
    #         # todo these are what we need to pass to sanding generate, currently sending list?
    #         panel_no += 1
    #
    #         xpos_pixels = scale_dim_to_pixels(image_width_pixels, real_width_in, xpos)
    #         ypos_pixels = scale_dim_to_pixels(image_height_pixels, real_height_in, ypos)
    #         cv2.rectangle(image, (xpos_pixels, ypos_pixels), (xpos_pixels + op_width_pixels, ypos_pixels + op_height_pixels), (0, 255, 255), 4)
    #         cv2.putText(image, f'Panel: {operation.tool_id}', (xpos_pixels + 30, ypos_pixels + 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)
    #         # now we have to draw the outlines of the operation on the image
    #         outlines = operation.get_outlines()
    #         for pt1, pt2 in outlines:
    #             pt1 = (scale_dim_to_pixels(image_width_pixels, real_width_in, pt1[0]),
    #                    scale_dim_to_pixels(image_height_pixels, real_height_in, pt1[1]))
    #             pt2 = (scale_dim_to_pixels(image_width_pixels, real_width_in, pt2[0]),
    #                    scale_dim_to_pixels(image_height_pixels, real_height_in, pt2[1]))
    #             # cv2.line(image, pt1, pt2, (0, 255, 0), 3)
    #             # cv2.putText(image, 'outline', (pt1[0], pt1[1]), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 1)
    #
    # # image = cv2.flip(image, 0) # flipped so part display starts at bottom left
    # image = cv2.flip(image, 0)
    return image
