import numpy as np
import cv2
import sys

import argparse
import time
import json


def pose_esitmation(frame, aruco_dict_type, matrix_coefficients, distortion_coefficients):

    '''
    frame - Frame from the video stream
    matrix_coefficients - Intrinsic matrix of the calibrated camera
    distortion_coefficients - Distortion coefficients associated with your camera
    return:-
    frame - The frame with the axis drawn on it
    '''

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray,5)
    # gray = cv2.GaussianBlur(gray,(5,5),0)
    cv2.aruco_dict = cv2.aruco.Dictionary_get(aruco_dict_type)
    parameters = cv2.aruco.DetectorParameters_create()


    corners, ids, rejected_img_points = cv2.aruco.detectMarkers(gray, cv2.aruco_dict, parameters=parameters,)
    # print(rejected_img_points)
    
    # bboxs, ids, rejected = cv2.aruco.detectMarkers(gray, arucoDict, parameters=arucoParam)

        # If markers are detected
    if len(corners) > 0:
        for i in range(0, len(ids)):
            # Estimate pose of each marker and return the values rvec and tvec---(different from those of camera coefficients)
            rvec, tvec, markerPoints = cv2.aruco.estimatePoseSingleMarkers(corners[i], 186, matrix_coefficients,
                                                                       distortion_coefficients)
            # Draw a square around the markers
            cv2.aruco.drawDetectedMarkers(frame, corners) 

            # Draw Axis
            cv2.drawFrameAxes(frame, matrix_coefficients, distortion_coefficients, rvec, tvec, 0.01)  
    print(rvec)
            

    return frame

if __name__ == '__main__':

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
    print(mtx)
    print(dist)
    
    k = mtx
    d = dist

    video = cv2.VideoCapture(0)
    video.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    video.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    time.sleep(2.0)

    while True:
        ret, frame = video.read()

        if not ret:
            break
        
        output = pose_esitmation(frame, cv2.aruco.DICT_ARUCO_ORIGINAL, k, d)

        cv2.imshow('Estimated Pose', output)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    video.release()
    cv2.destroyAllWindows()