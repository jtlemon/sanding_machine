import logging
import os

from apps.commons import SupportedMachines
from . import machine_ranges
from .constants_types import AppSupportedOperations, AppSupportedSettingValues, WidgetsType

CURRENT_MACHINE = SupportedMachines.dovetailMachine

from custom_widgets import SpinUnitMode

SUPPORTED_OPERATIONS = [
    AppSupportedOperations.dovetailCameraOperation,
    AppSupportedOperations.jointProfilesOperation,
    AppSupportedOperations.dowelsProfileOperation,
    AppSupportedOperations.bitProfilesOperation,
    AppSupportedOperations.settingParametersOperation
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

DOVETAIL_BIT_PROFILES_CONFIGURATION = [
    {
        "lbl": "Bit #",
        "target_key": "bit_profile_number",
        "field_type": WidgetsType.rangeWidget,
        "range": machine_ranges.bit_profile_number
    },
    {
        "lbl": "Bit length",
        "target_key": "bit_profile_length",
        "field_type": WidgetsType.rangeWidget,
        "range": machine_ranges.bit_profile_length
    },
    {
        "lbl": "Bit diameter",
        "target_key": "bit_profile_diameter",
        "field_type": WidgetsType.rangeWidget,
        "range": machine_ranges.bit_profile_diameter
    },
    {
        "lbl": "Cutting edge length",
        "target_key": "bit_profile_cutting_edge_length",
        "field_type": WidgetsType.rangeWidget,
        "range": machine_ranges.bit_profile_cutting_edge_length
    },
    {
        "lbl": "Number of flutes",
        "target_key": "bit_profile_number_of_flutes",
        "field_type": WidgetsType.rangeWidget,
        "range": machine_ranges.bit_profile_number_of_flutes
    },
    {
        "lbl": "Feed speed",
        "target_key": "bit_profile_feed_speed",
        "field_type": WidgetsType.speedWidget,
        "range": machine_ranges.bit_profile_feed_speed,
        "unit": "RPM"
    },
    {
        "lbl": "Spindle speed",
        "target_key": "bit_profile_spindle_speed",
        "field_type": WidgetsType.speedWidget,
        "range": machine_ranges.bit_profile_spindle_speed,
        "custom_lbl": {SpinUnitMode.MM_MODE: "mm/m", SpinUnitMode.IN_MODE: "IPM"}

    },
    {
        "lbl": "Bit type",
        "target_key": "bit_profile_bit_type",
        "field_type": WidgetsType.optionWidget,
        "options": ["dovetail", "drill bit", "box joint bit"],

    },

]

DOVETAIL_SETTING_CONFIGURATION = [
    {
        "lbl": "Standard width 1",
        "target_key": "dovetail_setting_standard_width_1",
        "field_type": WidgetsType.rangeWidget,
        "range": machine_ranges.dovetail_setting_standard_width_1
    },
    {
        "lbl": "Standard width 2",
        "target_key": "dovetail_setting_standard_width_2",
        "field_type": WidgetsType.rangeWidget,
        "range": machine_ranges.dovetail_setting_standard_width_2
    },
    {
        "lbl": "Standard width 3",
        "target_key": "dovetail_setting_standard_width_3",
        "field_type": WidgetsType.rangeWidget,
        "range": machine_ranges.dovetail_setting_standard_width_3
    },
    {
        "lbl": "Standard width 4",
        "target_key": "dovetail_setting_standard_width_4",
        "field_type": WidgetsType.rangeWidget,
        "range": machine_ranges.dovetail_setting_standard_width_4
    },
    {
        "lbl": "X zero",
        "target_key": "dovetail_setting_x_zero",
        "field_type": WidgetsType.rangeWidget,
        "range": machine_ranges.dovetail_setting_x_zero
    },
    {
        "lbl": "Y zero",
        "target_key": "dovetail_setting_y_zero",
        "field_type": WidgetsType.rangeWidget,
        "range": machine_ranges.dovetail_setting_y_zero
    },
    {
        "lbl": "Z zero",
        "target_key": "dovetail_setting_z_zero",
        "field_type": WidgetsType.rangeWidget,
        "range": machine_ranges.dovetail_setting_z_zero
    },
    {
        "lbl": "A zero",
        "target_key": "dovetail_setting_a_zero",
        "field_type": WidgetsType.rangeWidget,
        "range": machine_ranges.dovetail_setting_a_zero
    },
    {
        "lbl": "B zero",
        "target_key": "dovetail_setting_b_zero",
        "field_type": WidgetsType.rangeWidget,
        "range": machine_ranges.dovetail_setting_b_zero
    },
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
