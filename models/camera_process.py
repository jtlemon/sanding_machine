from multiprocessing import Process, Event, Value, Lock, Queue
import cv2
import time
import threading
from configurations import common_configurations
import json
import numpy as np

class CameraManger:
    def __init__(self, cam_index):
        self.__cam_index = cam_index
        self.__close_event = threading.Event()
        self.__latest_image = None
        self.__is_camera_running = False
        self.__thread_handler = None
        self.__cam = None

    def __main__loop(self):
        self.__cam = cv2.VideoCapture(self.__cam_index, cv2.CAP_V4L2)
        self.__cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        self.__cam.set(cv2.CAP_PROP_FPS, common_configurations.FRAME_RATE)
        self.__cam.set(cv2.CAP_PROP_FRAME_WIDTH, common_configurations.IMAGE_WIDTH)
        self.__cam.set(cv2.CAP_PROP_FRAME_HEIGHT, common_configurations.IMAGE_HEIGHT)
        self.__cam.set(cv2.CAP_PROP_BUFFERSIZE, 3)
        time.sleep(1)
        if self.__cam.isOpened():
            self.__is_camera_running = True
        else:
            return
        frame_loss_counter = 0
        while not self.__close_event.is_set():
            is_valid, image = self.__cam.read()
            if is_valid:
                frame_loss_counter = 0
                #image = cv2.rotate(image, cv2.ROTATE_180)
                self.__latest_image = image
            else:
                frame_loss_counter += 1
                if frame_loss_counter > 20:
                    self.__close_event.set()
            self.__close_event.wait(0.1)
        # try to close the camera
        try:
            self.__cam.release()
        except Exception as e :
            pass
        self.__cam = None
        self.__is_camera_running = False

    def get_image(self):
        return None if self.__latest_image is None else self.__latest_image.copy()

    def stop_stream(self):
        self.__close_event.set()

    def start_stream(self):
        if self.__is_camera_running:
            return
        self.__close_event.clear()
        self.__thread_handler = threading.Thread(target=self.__main__loop)
        self.__thread_handler.start()

    def is_stream_running(self):
        return self.__is_camera_running

    def th_join(self):
        self.__thread_handler.join()


class CameraOnly:
    def __init__(self, cam_index):
        self.__cam_index = cam_index
        self.__latest_image = None
        self.__is_camera_running = False
        self.__cam = None
        self.frame_loss_counter = 0
        mtx_json = open('configurations/custom_configurations/camera_matrix.json')
        # returns JSON object as
        # a dictionary
        data = json.load(mtx_json)
        self.mtx = np.array([[data['fx'],0,data['cx']],[0,data['fy'],data['cy']],[0,0,1]])
        mtx_json.close()
        dist_json = open('configurations/custom_configurations/camera_dist.json')
        # returns JSON object as
        # a dictionary
        data = json.load(dist_json)
        self.dist = np.array([[data["k1"],data["k2"],data["p1"],data["p2"],data["k3"]]])
        dist_json.close()
        print(self.mtx)
        print(self.dist)

    def connect(self):
        self.__cam = cv2.VideoCapture(self.__cam_index, cv2.CAP_V4L2)
        self.__cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        self.__cam.set(cv2.CAP_PROP_FPS, common_configurations.FRAME_RATE)
        self.__cam.set(cv2.CAP_PROP_FRAME_WIDTH, common_configurations.IMAGE_WIDTH)
        self.__cam.set(cv2.CAP_PROP_FRAME_HEIGHT, common_configurations.IMAGE_HEIGHT)
        self.__cam.set(cv2.CAP_PROP_BUFFERSIZE, 3)
        if self.__cam.isOpened():
            self.__is_camera_running = True

    def read_cycle(self):
        if self.__cam.isOpened():
            is_valid, image = self.__cam.read()
            if is_valid:
                self.frame_loss_counter = 0
                image = cv2.undistort(image, self.mtx, self.dist, None, self.mtx)
                image = cv2.resize(image, (common_configurations.IMAGE_HEIGHT,
                                           common_configurations.IMAGE_WIDTH
                                    ))
                # 
                #image = cv2.rotate(image, cv2.ROTATE_180)
                return  cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                self.frame_loss_counter += 1
                return None
        else:
            return None

    def close_cam(self):
        try:
            self.__cam.release()
        except Exception as e :
            pass
        self.__cam = None


class CameraMangerProcess(Process):
    process_close_event = Event()
    images_queue = [Queue(maxsize=4) for i in range(common_configurations.AVAILABLE_CAMERAS)]
    @staticmethod
    def run():
        sys_cameras_list = [CameraOnly(i) for i in range(common_configurations.AVAILABLE_CAMERAS)]
        for cam in sys_cameras_list:
            cam.connect()
        while not CameraMangerProcess.process_close_event.is_set():
            time.sleep(1/common_configurations.FRAME_RATE)
            for index, cam in enumerate(sys_cameras_list):
                image = cam.read_cycle()
                if not (image is None):
                    queue_ref = CameraMangerProcess.images_queue[index]
                    if queue_ref.full():
                        queue_ref.get()
                    queue_ref.put(image)
        # release camera
        for cam in sys_cameras_list:
            cam.close_cam()


    @staticmethod
    def get_image(cam_index:int):
        if cam_index < common_configurations.AVAILABLE_CAMERAS:
            queue_ref = CameraMangerProcess.images_queue[cam_index]
            if not queue_ref.empty():
                return queue_ref.get()
    @staticmethod
    def close_service():
        CameraMangerProcess.process_close_event.set()