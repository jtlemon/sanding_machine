from multiprocessing import Process, Event, Value, Lock, Queue
from collections import deque
from threading import Thread, Event, Lock
from queue import Queue
import cv2
import time
import threading
from configurations import common_configurations

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

    def connect(self):
        self.__cam = cv2.VideoCapture(self.__cam_index)
        #self.__cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
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
                image = cv2.resize(image, (common_configurations.IMAGE_HEIGHT,
                                           common_configurations.IMAGE_WIDTH
                                    ))
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


class CameraMangerProcess(Thread):
    process_close_event = Event()
    images_queue = [list() for i in range(common_configurations.AVAILABLE_CAMERAS)]

    @staticmethod
    def run():
        sys_cameras_list = [CameraOnly(i) for i in range(common_configurations.AVAILABLE_CAMERAS)]
        for cam in sys_cameras_list:
            cam.connect()
        while True :
            time.sleep(1/common_configurations.FRAME_RATE)
            for index, cam in enumerate(sys_cameras_list):
                image = cam.read_cycle()

                if not (image is None):
                    queue_ref = CameraMangerProcess.images_queue[index]
                    if len(queue_ref) == 4:
                        queue_ref.pop(0)
                    queue_ref.append(image)
        # release camera
        for cam in sys_cameras_list:
            cam.close_cam()


    @staticmethod
    def get_image(cam_index:int):
        if cam_index < common_configurations.AVAILABLE_CAMERAS:
            queue_ref = CameraMangerProcess.images_queue[cam_index]
            if len(queue_ref) > 0:
                return queue_ref[0]

    @staticmethod
    def close_service():
        print("hello world .......")
        CameraMangerProcess.process_close_event.set()