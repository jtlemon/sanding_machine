import cv2
import numpy as np
import glob
import json

# Developed by Bhavin started 11/1/2023

# This code calibrate the intrinsic p[arameters of the camera]
class CameraIntrinsicCalibrator:
    def __init__(self,square_size, grids, file_path, image_format, show_image_time):
        self.squareSize = square_size
        self.grids = grids
        self.file_path = file_path
        self.imageFormat = image_format
        self.show_image_time = show_image_time
        self.criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        self.objp = np.zeros((self.grids[0] * self.grids[1], 3), np.float32)
        self.objp[:, :2] = np.mgrid[0:self.grids[0], 0:self.grids[1]].T.reshape(-1, 2)
        self.objp = self.objp * self.squareSize
        self.objpoints = []  # 3d point in real world space
        self.imgpoints = []
        self.images = glob.glob(self.file_path + '/*.' + self.imageFormat)
        print(self.file_path + '/*.' + self.imageFormat)
        for fname in self.images:
            img = cv2.imread(fname)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Find the chess board corners
            ret, corners = cv2.findChessboardCorners(gray, (self.grids[0], self.grids[1]), None)

            # If found, add object points, image points (after refining them)
            if ret == True:
                self.objpoints.append(self.objp)

                cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), self.criteria)
                self.imgpoints.append(corners)

                # Draw and display the corners

                cv2.drawChessboardCorners(img, (self.grids[0], self.grids[1]), corners, ret)
                img = cv2.resize(img, (640, 600), interpolation=cv2.INTER_AREA)
                #cv2.imshow('img Checkerboard', img)
                #cv2.waitKey(show_image_time)
        #cv2.destroyAllWindows()
        _, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(self.objpoints, self.imgpoints, gray.shape[::-1], None, None)
        self.mtx = mtx
        self.dist = dist
        #np.savetxt('camera_params/camera_intrinsics/mtx1.csv', mtx, delimiter=',')
        #np.savetxt('camera_params/camera_intrinsics/dist1.csv', dist, delimiter=',')

        mean_error = 0
        for i in range(len(self.objpoints)):
            imgpoints2, _ = cv2.projectPoints(self.objpoints[i], rvecs[i], tvecs[i], mtx, dist)
            error = cv2.norm(self.imgpoints[i], imgpoints2, cv2.NORM_L2) / len(imgpoints2)
            mean_error += error
        print("total error: {}".format(mean_error / len(self.objpoints)))

    def return_mtx(self):
        return self.mtx

    def return_dist(self):
        return self.dist



# Below is example for how to run the code
if __name__ == '__main__':
    
    path = '/home/sanding/chess_board'
    calibrate = CameraIntrinsicCalibrator(22.66 ,(9,6),path,'jpg',300)
    mtx = calibrate.return_mtx()
    dist = calibrate.return_dist()
    print(mtx)
    print(dist)
    mtx_dict = {'fx': mtx[0][0],
                'fy': mtx[1][1],
                'cx': mtx[0][2],
                'cy': mtx[1][2]}

    dist_dict = {'k1': dist[0][0],
                 'k2': dist[0][1],
                 'p1': dist[0][2],
                 'p2': dist[0][3],
                 'k3': dist[0][4]}

mtx_json_object = json.dumps(mtx_dict, indent=4)
 
# Writing to sample.json
with open("/home/sanding/dovetail_drill_dowel/configurations/custom_configurations/camera_matrix.json", "w") as outfile:
    outfile.write(mtx_json_object)

dist_json_object = json.dumps(dist_dict, indent=4)
 
# Writing to sample.json
with open("/home/sanding/dovetail_drill_dowel/configurations/custom_configurations/camera_dist.json", "w") as outfile:
    outfile.write(dist_json_object)

cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

if not cap.isOpened():
    raise IOError("Cannot open webcam")

while True:

    ret, frame = cap.read()
    
    
    dst = cv2.undistort(frame, mtx, dist, None, mtx)

    cv2.imshow('Undistorted Image', dst)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
