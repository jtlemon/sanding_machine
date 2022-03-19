import os
import logging
from apps.commons import SupportedMachines
CURRENT_MACHINE = SupportedMachines.sandingMachine
# ************************* dovetail left/right active mapper *************
DOVETAIL_LEFT_RIGHT_ACTIVE_LVL_MAPPER = [0, 4, 6, 8, 10]
DOVETAIL_SUPPORTED_LEVELS = 5  # the first lvl off
BASE_LEVEL_CONFIGURATION_KEY = "dovetail_setting_standard_width_"  # "dovetail_setting_standard_width_4" for lvl 4
# ******************************************** Errors ****************************
INSTALLED_ERRORS = {
    "type1": {"txt": "Door opened", "flashing": True, "color": "blue"},
    "type2": {"txt": "error message", "flashing": False, "color": "blue"},
    "machineerror": {"txt": "Machine Error", "flashing": True, "color": "red"}
}
# main logging info
LOGGER_BASE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "logs")
LOGGER_NAME = "Dovetail"

AVAILABLE_CAMERAS = 1
FRAME_RATE = 5  # we will take image every 0.1 sec
IMAGE_WIDTH = 480
IMAGE_HEIGHT = 640

# TEMPERATURE
TEMPERATURE_API_KEY = "bdde746d10436194809f0f822c5c1a2b"
MEASURE_TEMPERATURE_EVERY = 30

# sensors
IS_SENSOR_MODULE_ENABLED = False
SENSOR_MODULE_COM_PORT = "/dev/ttyUSB0"
SENSOR_MODULE_BAUD_RATE = 19200
SENSOR_LOGGER_FILE = "sensor_board_logs.logs"
SENSOR_LOGGING_LVL = logging.INFO
SENSOR_LOGGING_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
SENSOR_MAP = [101.6, 228.6, 304.8, 381, 457.2, 533.4, 609.6, 685.8, 762, 914.4]

# ***************************** E-Stop module ************************
IS_ESTOP_MODULE_ENABLED = False
ESTOP_MODULE_COM_PORT = "/dev/ttyACM0"
ESTOP_MODULE_BAUD_RATE = 4800
ESTOP_CHECK_STATUS_EVERY = 0.5  # check status every 0.5 sec

# ************************* grbl *********************
IS_GRBL_MODULE_ENABLED = True
GRBL_MODULE_COM_PORT = "/dev/ttyACM0"
