import numpy as np
import cv2
import json
import time
import open3d as o3d

from scipy.spatial.transform import Rotation as R

class MatrixPose:
    @staticmethod
    def pose_to_matrix(startpose):
        rot_mat = R.from_euler('ZYX', [startpose[3], startpose[4], startpose[5]], degrees=True)
        homogeneous_mat = np.array(
            [[rot_mat.as_matrix()[0][0], rot_mat.as_matrix()[0][1], rot_mat.as_matrix()[0][2], startpose[0]],
             [rot_mat.as_matrix()[1][0], rot_mat.as_matrix()[1][1], rot_mat.as_matrix()[1][2], startpose[1]],
             [rot_mat.as_matrix()[2][0], rot_mat.as_matrix()[2][1], rot_mat.as_matrix()[2][2], startpose[2]],
             [0, 0, 0, 1]])
        return homogeneous_mat

    @staticmethod
    def matrix_to_pose(matrix):
        rot_mat = R.from_matrix([[matrix[0][0], matrix[0][1], matrix[0][2]],
                                 [matrix[1][0], matrix[1][1], matrix[1][2]],
                                 [matrix[2][0], matrix[2][1], matrix[2][2]]])

        eulerang = rot_mat.as_euler('ZYX', degrees=True)

        pose = [matrix[0][3], matrix[1][3], matrix[2][3], eulerang[0], eulerang[1], eulerang[2]]
        return pose


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

def find_plane(point1, point2, point3):
    # p1 = np.array(point1)
    # p2 = np.array(point2)
    # p3 = np.array(point3)

    # # These two vectors are in the plane
    # v1 = p3 - p1
    # v2 = p2 - p1

    # # the cross product is a vector normal to the plane
    # cp = np.cross(v1, v2)
    # unit_cp = cp / np.linalg.norm(cp)
    # a, b, c = unit_cp

    # # This evaluates a * x3 + b * y3 + c * z3 which equals d
    # d = np.dot(cp, p3)
    # print(a, b, c, d)
    # vector1 = [point2[0] - point1[0], point2[1] - point1[1], point2[2] - point1[2]]
    # vector2 = [point3[0] - point1[0], point3[1] - point1[1], point3[2] - point1[2]]

    # cross_product = [vector1[1] * vector2[2] - vector1[2] * vector2[1], -1 * (vector1[0] * vector2[2] - vector1[2] * vector2[0]), vector1[0] * vector2[1] - vector1[1] * vector2[0]]

    # a = cross_product[0]
    # b = cross_product[1]
    # c = cross_product[2]
    # d = - (cross_product[0] * point1[0] + cross_product[1] * point1[1] + cross_product[2] * point1[2])
    pcd = o3d.geometry.PointCloud()
    pcd.points.append(point1)
    pcd.points.append(point2)
    pcd.points.append(point3)
    
    plane_model, inliers = pcd.segment_plane(distance_threshold=0.01,
                                         ransac_n=3,
                                         num_iterations=1000)
    [a, b, c, d] = plane_model


    return [a,b,c,d]


def get_undistorted_plane_point(u, v, camera_matrix, camera_distortion, plane):
    undistorted_points = cv2.undistortPoints(np.array([[u, v]], np.float32), camera_matrix, camera_distortion,
                                                P=camera_matrix)
    u_ = undistorted_points[0][0][0]
    v_ = undistorted_points[0][0][1]
    # print('undistorted:', u_, v_)
    fx = camera_matrix[0][0]
    cx = camera_matrix[0][2]
    fy = camera_matrix[1][1]
    cy = camera_matrix[1][2]
    a = plane[0]
    b = plane[1]
    c = plane[2]
    d = plane[3]

    x_ = (round(u_, 2) - cx) / fx
    y_ = (round(v_, 2) - cy) / fy
    z = -d / ((a * x_) + (b * y_) + c)
    x = z * x_
    y = z * y_
    return [x, y, z]



def create_transformation_frame(three_p):
    c1 = three_p[0]
    c2 = three_p[1]
    c3 = three_p[2]
    x_axis = [c2 - c1 for c2, c1 in zip(c2, c1)]
    x_axis = x_axis / np.linalg.norm(x_axis)
    z_axis = find_plane(c1, c2, c3)
    z_axis = -np.array(z_axis[0:3])
    print("z_axis:",z_axis)
    # z_axis = -z_axis
    y_axis = np.cross(z_axis, x_axis)
    y_axis = y_axis / np.linalg.norm(y_axis)
    rotmT = np.array([x_axis, y_axis, z_axis])
    # rotm = np.linalg.inv(rotmT)
    rotm = rotmT.transpose()
    # print(rotm)

    bTw = np.eye(4)
    bTw[0:3, 0:3] = rotm
    bTw[0:3, 3] = c1

    return bTw

if __name__ == '__main__':

    #find aruco
    mtx_json = open('/home/sanding/dovetail_drill_dowel/configurations/custom_configurations/camera_matrix.json')
    # returns JSON object as
    # a dictionary
    data = json.load(mtx_json)
    mtx = np.array([[data['fx'],0,data['cx']],[0,data['fy'],data['cy']],[0,0,1]])
    mtx_json.close()
    dist_json = open('/home/sanding/dovetail_drill_dowel/configurations/custom_configurations/camera_dist.json')
    # returns JSON object as
    # a dictionary
    data = json.load(dist_json)
    dist = np.array([[data["k1"],data["k2"],data["p1"],data["p2"],data["k3"]]])
    dist_json.close()
    # print(mtx)
    # print(dist)
    
    k = mtx
    d = dist

    video = cv2.VideoCapture(0)
    video.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    video.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    time.sleep(2.0)

    
    ret, frame = video.read()
    ret, frame = video.read()
    ret, frame = video.read()
   

    video.release()
    cv2.destroyAllWindows()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray,5)
    # gray = cv2.GaussianBlur(gray,(5,5),0)
    cv2.aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_ARUCO_ORIGINAL)
    parameters = cv2.aruco.DetectorParameters_create()


    corners, ids, rejected_img_points = cv2.aruco.detectMarkers(gray, cv2.aruco_dict, parameters=parameters,)
    # print(rejected_img_points)
    print(corners)
    # bboxs, ids, rejected = cv2.aruco.detectMarkers(gray, arucoDict, parameters=arucoParam)

        # If markers are detected
    print((corners[0][0][0][0],corners[0][0][0][1]))
    cv2.circle(frame,(int(corners[0][0][0][0]),int(corners[0][0][0][1])),10,(0,255,0),10)
    # cv2.imshow('frame',frame)
    # cv2.waitKey(0)
    print(corners[0])
    rvec, tvec, markerPoints = cv2.aruco.estimatePoseSingleMarkers(corners[0], 186, mtx,
                                                                       dist)
    rotm = cv2.Rodrigues(rvec)[0]

    print(rotm)
    print(tvec)

    cTa = np.eye(4)

    cTa[0:3,0:3] = rotm
    cTa[0:3,3] = tvec[0][0] 

    print("transformation:", cTa)
    pose = MatrixPose.matrix_to_pose(cTa)
    print('pose:', pose)

    # cTa = np.linalg.inv(cTa)
    point11 = [0,0,-6.35,1]
    point21 = [300,0,-6.35,1]
    point31 = [300,300,-6.35,1]

    point1 = cTa @ point11
    point2 = cTa @ point21
    point3 = cTa @ point31

    print("Points:")
    print("point1: ", point1)
    print("point2: ", point2)
    print("point3: ", point3)




    plane = find_plane(point1[0:3], point2[0:3], point3[0:3])
    print("plane:", plane)
    mouse_points = [[290, 869],[1342 ,865],[295 ,400]]
    



    # def draw_circle(event,x,y,flags,param):
    #     global mouse_points
    #     global frame
    #     if event == cv2.EVENT_LBUTTONDBLCLK:
    #         cv2.circle(frame,(x,y),5,(255,0,0),-1)
    #         print(x,y)
    #         mouse_points.append([x,y])

    # cv2.namedWindow('image')
    # cv2.setMouseCallback('image',draw_circle)

    # while(1):
    #     cv2.imshow('image',frame)
    #     k = cv2.waitKey(20) & 0xFF
    #     if k == 27:
    #         break
    #     elif k == ord('a'):
    #         print(mouse_points)

    




    three_p = []
    for p in mouse_points:
        three_p.append(get_undistorted_plane_point(p[0],p[1],mtx,dist,plane))
        print("point:::::")
        print(get_undistorted_plane_point(p[0],p[1],mtx,dist,plane))

    
    cTcnc = create_transformation_frame(three_p)
    print(cTcnc)
    print(MatrixPose.matrix_to_pose(cTcnc))


    mesh_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(
        size=500, origin=[0, 0, 0])

    cTa_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(
        size=500, origin=[0, 0, 0])
    cTa_frame.transform(cTa)
    cTa_frame.paint_uniform_color([0,1,0])

    cTcnc_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(
        size=100, origin=[0, 0, 0])
    cTcnc_frame.transform(cTcnc)
    # cTcnc_frame.paint_uniform_color([1,0,0])

    # o3d.visualization.draw_geometries([mesh_frame,cTa_frame,cTcnc_frame])


   
    u,v = project_3d_to_image(three_p[0], mtx, dist[0])
    print(u,v)
   

#     [[ 9.99926092e-01 -4.78753531e-03 -1.11754220e-02 -8.95281255e+02]
#  [-4.07404801e-03 -9.98004185e-01  6.30162665e-02  4.66110891e+02]
#  [-1.14548105e-02 -6.29660799e-02 -9.97949929e-01  7.47481826e+03]
#  [ 0.00000000e+00  0.00000000e+00  0.00000000e+00  1.00000000e+00]]
# [-895.2812545577443, 466.1108905587368, 7474.818257005325, -0.23344171808966493, 0.6563266525603568, -176.38968400879827]


    #generate 3 points on aruco's x,y plane 
    #create plane
    #mouse click on 3 points to create x,y,z coordinates of machine
    # this gives out machine coordinates w.r.t camera.
    #using parts length project back points in image





