import logging
import os

from . import machine_ranges
from apps.commons import SupportedMachines
from .constants_types import AppSupportedOperations, AppSupportedSettingValues, WidgetsType

CURRENT_MACHINE = SupportedMachines.dovetailMachine

SUPPORTED_OPERATIONS = [
    AppSupportedOperations.dovetailCameraOperation,
    AppSupportedOperations.jointProfilesOperation,
    AppSupportedOperations.dowelsProfileOperation
]
SUPPORTED_SETTING_VALUES = {
    AppSupportedSettingValues.standardWidth1,
    AppSupportedSettingValues.standardWidth2,
    AppSupportedSettingValues.standardWidth3,
    AppSupportedSettingValues.standardWidth4
}
# ******************************** dovetail Joint profiles configurations ***********************


DOVETAIL_JOINT_PROFILE_CONFIGURATION = [
    {"lbl": "Pin spacing", "target_key": "joint_profile_pin_spacing",
     "range": machine_ranges.joint_profile_pin_spacing},
    {"lbl": "Depth", "target_key": "joint_profile_depth", "range": machine_ranges.joint_profile_depth},
    {"lbl": "Bit height", "target_key": "joint_profile_bit_height", "range": machine_ranges.joint_profile_bit_height},
    {"lbl": "Pin width", "target_key": "joint_profile_bit_width", "range": machine_ranges.joint_profile_bit_width},
    {"lbl": "Distance from bottom", "target_key": "joint_profile_distance_from_bottom",
     "range": machine_ranges.joint_profile_distance_from_bottom},
]


DOVETAIL_DOWEL_JOINT_PROFILE_CONFIGURATION = [
    {
        "lbl": "Spacing",
        "target_key": "dowel_profile_spacing",
        "field_type": WidgetsType.rangeWidget,
        "range": machine_ranges.dowel_profile_spacing
    },
    {
        "lbl": "Distance from edge",
        "target_key": "dowel_profile_dis_from_edge",
        "field_type": WidgetsType.rangeWidget,
        "range": machine_ranges.dowel_profile_dis_from_edge
    },
    {
        "lbl": "Distance from face",
        "target_key": "dowel_profile_dis_from_face",
        "field_type": WidgetsType.rangeWidget,
        "range": machine_ranges.dowel_profile_dis_from_face
    },
    {
        "lbl": "Face depth",
        "target_key": "dowel_profile_face_depth",
        "field_type": WidgetsType.rangeWidget,
        "range": machine_ranges.dowel_profile_face_depth
    },
    {
        "lbl": "Edge depth",
        "target_key": "dowel_profile_edge_depth",
        "field_type": WidgetsType.rangeWidget,
        "range": machine_ranges.dowel_profile_edge_depth
    }
]

# main logging info
LOGGER_BASE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "logs")
LOGGER_NAME = "Dovetail"

DOVETAIL_SUPPORTED_LEVELS = 4
AVAILABLE_CAMERAS = 1
FRAME_RATE = 5  # we will take image every 0.1 sec
IMAGE_WIDTH = 720
IMAGE_HEIGHT = 420

# TEMPERATURE
TEMPERATURE_API_KEY = "bdde746d10436194809f0f822c5c1a2b"
MEASURE_TEMPERATURE_EVERY = 30

# sensors
IS_SENSOR_MODULE_ENABLED = False
SENSOR_MODULE_COM_PORT = "/dev/ttyACM0"
SENSOR_MODULE_BAUD_RATE = 9600
SENSOR_LOGGER_FILE = "sensor_board_logs.logs"
SENSOR_LOGGING_LVL = logging.INFO
SENSOR_LOGGING_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
SENSOR_MAP = [101.6, 228.6, 304.8, 381, 457.2, 533.4, 609.6, 685.8, 762, 914.4]
