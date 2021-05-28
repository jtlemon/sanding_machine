import logging
from PySide2 import QtCore
from .sensors_connector_bsp import SensorsSerialConnector
import configurations.static_app_configurations as app_config

module_logger  = logging.getLogger(app_config.LOGGER_NAME)

class SensorConnector(QtCore.QObject):
    weightChangedSignal = QtCore.Signal(float)
    newWidthSensorsSignal = QtCore.Signal(list)
    autoLeftRightWidthChanged = QtCore.Signal(float, float)
    physicalStartSignal = QtCore.Signal(str) # this simulate the left and right btn
    physicalErrorSignal = QtCore.Signal(str)
    def __init__(self):
        super(SensorConnector, self).__init__()
        self.sensor_vals = {
            0: {"state": False, "msg": "start2"},
            1: {"state": False, "msg": "y-axis error"},
            2: {"state": False, "msg": "z-axis error"},
            3: {"state": False, "msg": "emergency status"},
            4: {"state": False, "msg": "emergency stop"},
            5: {"state": False, "msg": "start"},
        }
        self.auto_right_width = 0
        self.auto_left_width = 0
        self.__width_sensor_readings = list()
        self.__current_measured_weight = 0.0
        self.__serial_interface_thread = SensorsSerialConnector()
        self.__serial_interface_thread.weightChanged.connect(self.handle_weight_changed)
        self.__serial_interface_thread.newReading.connect(self.handle_new_sensor_readings_received)

    def start(self):
        self.__serial_interface_thread.start()

    def handle_weight_changed(self, new_weight):
        pass

    def get_weight(self):
        return self.__current_measured_weight

    def handle_new_sensor_readings_received(self, readings):
        for i in range(6):
            if readings[i] != self.sensor_vals[i]['state']:
                self.sensor_vals[i]['state'] = readings[i]
                if readings[i]:
                    if i == 5:
                        self.physicalStartSignal.emit("left")
                        module_logger.debug("left physical button clicked")
                    elif i == 0:
                        self.physicalStartSignal.emit("right")
                        module_logger.debug("right physical button clicked")
                    else:
                        self.physicalErrorSignal.emit(self.sensor_vals[i]['msg'])
        sensor_readings = readings[6:16]
        if not self._lists_equal(sensor_readings, self.__width_sensor_readings):
            self.__width_sensor_readings = sensor_readings
            # calculate the width
            self.get_width_from_sensors(sensor_readings)
            self.autoLeftRightWidthChanged.emit(self.auto_left_width, self.auto_right_width)
            self.newWidthSensorsSignal.emit(sensor_readings)

    def _lists_equal(self, l1, l2):
        if len(l1) != len(l2):
            return False
        for i in range(len(l1)):
            if l1[i] != l2[i]:
                return False
        return True

    def get_width_from_sensors(self, array_of_sensor):
        array_of_sensor = array_of_sensor.copy()
        sensors_counts = len(array_of_sensor)
        if array_of_sensor[0] and array_of_sensor[sensors_counts - 1]:
            return "error"
        elif array_of_sensor[0] == 0 and array_of_sensor[sensors_counts - 1] == 0:
            self.auto_left_width = 0
            self.auto_right_width = 0
            return "no reading"
        else:
            active_dir = "left"
            if array_of_sensor[sensors_counts - 1]:
                array_of_sensor.reverse()
                active_dir = "right"
            last_one = 0
            for i in range(sensors_counts):
                if array_of_sensor[i] == 1:
                    last_one = i
            if active_dir == "right":
                self.auto_right_width = app_config.SENSOR_MAP[last_one]
            else:
                self.auto_left_width = app_config.SENSOR_MAP[last_one]
            return app_config.SENSOR_MAP[last_one], active_dir

    def close_service(self):
        self.__serial_interface_thread.requestInterruption()

    def control_servo_state(self, is_on):
        if is_on is True:
            self.__serial_interface_thread.turn_on_servo()
        else:
            self.__serial_interface_thread.turn_off_servo()