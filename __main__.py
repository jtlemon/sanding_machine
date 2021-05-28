import os, sys
try:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
except Exception as e:
    print(e)
from PySide2 import QtWidgets, QtGui, QtCore
from models import  CameraMangerProcess
from view_managers import JointProfilesPageManager, DovetailCameraPageManager
from views import MachineInterfaceUi
from configurations import static_app_configurations,AppSupportedOperations
import time
from models.temperature_service import TemperatureService
from models.sensors_connector_hal import SensorConnector
from models.grbl_hal import GrblControllerHal


class MachineGuiInterface(MachineInterfaceUi):
    def __init__(self):
        super(MachineGuiInterface, self).__init__()
        self.__camera_image_subscribers = {index:list() for index in range(static_app_configurations.AVAILABLE_CAMERAS)}
        self.__joint_profile_update_subscribers = list()
        self.__installed_operations = {}
        for app_operation in static_app_configurations.SUPPORTED_OPERATIONS:
            operation_page_widget = None
            if app_operation == static_app_configurations.AppSupportedOperations.dovetailCameraOperation:
                operation_page_widget = DovetailCameraPageManager("Camera")
                self.subscribe_to_image(0, operation_page_widget)
                self.__joint_profile_update_subscribers.append(operation_page_widget)
            elif app_operation == static_app_configurations.AppSupportedOperations.jointProfilesOperation:
                operation_page_widget = JointProfilesPageManager()
                operation_page_widget.jointProfilesUpdatedSignal.connect(self.handle_joint_profile_updates)
            self.add_app_window_widget(operation_page_widget)
            self.__installed_operations[app_operation] = operation_page_widget

        # default
        self.__temperature_thread = TemperatureService()
        # display sensor values also and weight auto width, height in certain dovetail widget if it's existed
        self.__sensors_board_thread = SensorConnector()
        self.__grbl_interface = GrblControllerHal()

        # connect signals
        self.__temperature_thread.new_temperature.connect(
            lambda display_weather, weather_icon: self.set_current_temperature(display_weather, weather_icon))

        self.__sensors_board_thread.physicalErrorSignal.connect(self.__grbl_interface.handle_physical_error_signal)
        self.__sensors_board_thread.autoLeftRightWidthChanged.connect(self.__grbl_interface.handle_auto_left_right_width_changed)
        # this to control on/of servo
        self.__grbl_interface.servoStartSignal.connect(self.__sensors_board_thread.control_servo_state)

        # camera
        self.__camera_check_timer = QtCore.QTimer()
        self.__camera_check_timer.timeout.connect(self.check_available_images)
        self.__camera_check_timer.start(int(1000/static_app_configurations.FRAME_RATE))

        # initiate all signals
        if AppSupportedOperations.jointProfilesOperation in static_app_configurations.SUPPORTED_OPERATIONS:
            available_profile_names = self.__installed_operations[AppSupportedOperations.jointProfilesOperation].get_profile_names()
            self.handle_joint_profile_updates(available_profile_names)
        # start all threads
        self.__temperature_thread.start()
        self.__sensors_board_thread.start()
        self.__grbl_interface.start_process()



    def subscribe_to_image(self, index, widget):
        if index in self.__camera_image_subscribers:
            self.__camera_image_subscribers[index].append(widget)


    def check_available_images(self):
        for cam_index in range(static_app_configurations.AVAILABLE_CAMERAS):
            subscribers_list = self.__camera_image_subscribers[cam_index]
            if len(subscribers_list) > 0:
                active_widget = None
                for subscriber_widget in subscribers_list:
                    if self.get_current_active_widget() == subscriber_widget:
                        active_widget = subscriber_widget
                if active_widget is None:
                    continue
                image = camera_process.get_image(cam_index)
                if image is None:
                    continue
                # convert image to pix mab
                height, width, channel = image.shape
                bytes_per_line = 3 * width
                q_image = QtGui.QImage(image.data, width, height, bytes_per_line, QtGui.QImage.Format_RGB888)
                pix_map = QtGui.QPixmap.fromImage(q_image)
                active_widget.new_image_received(cam_index, pix_map)

    def handle_joint_profile_updates(self, new_profiles):
        for subscriber_widget in self.__joint_profile_update_subscribers:
            subscriber_widget.handle_joint_profile_updated(new_profiles)

    def closeEvent(self, event) -> None:
        self.__temperature_thread.close_service()
        self.__sensors_board_thread.close_service()
        self.__grbl_interface.release_resources()



if __name__ == "__main__":
    from views import utils
    camera_process = CameraMangerProcess()
    camera_process
    camera_process.start()
    app = QtWidgets.QApplication(sys.argv)
    utils.load_app_fonts()
    machine_gui_interface = MachineGuiInterface()
    machine_gui_interface.showMaximized()
    app.setStyleSheet(utils.load_app_style())
    app.exec_()
    camera_process.close_service()
    time.sleep(1)
    sys.exit(0)

