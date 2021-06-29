import logging
import os

from apps.commons import SupportedMachines
from . import machine_ranges
from .constants_types import AppSupportedOperations, AppSupportedSettingValues, WidgetsType

CURRENT_MACHINE = SupportedMachines.dovetailMachine

from custom_widgets import SpinUnitMode

SUPPORTED_OPERATIONS = [
    AppSupportedOperations.dovetailCameraOperation,
    AppSupportedOperations.jointDowelBitProfilesOperation,
    AppSupportedOperations.bitProfilesOperation,
    AppSupportedOperations.restMachineOperation,
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
    {"lbl": "Bit height", "target_key": "joint_profile_bit_height", "range": machine_ranges.joint_profile_bit_height},
    {"lbl": "Distance from bottom", "target_key": "joint_profile_distance_from_bottom",
     "range": machine_ranges.joint_profile_distance_from_bottom},
    {"lbl": "Material Thickness", "target_key": "joint_profile_material_thickness",
     "range": machine_ranges.joint_profile_material_thickness},
]
DOVETAIL_JOINT_PROFILE_OPTIONS = [
    {"lbl": "Adjust Depth", "target_key": "joint_deep_adjustment",
     "field_type": WidgetsType.rangeWidget,
     "range": machine_ranges.joint_deep_adjustment},
    {"lbl": "Adjust Tightness", "target_key": "joint_tightness_adjustment",
     "field_type": WidgetsType.rangeWidget,
     "range": machine_ranges.joint_deep_adjustment}
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
DOVETAIL_DOWEL_PROFILE_OPTIONS = [
    {"lbl": "Opt1", "target_key": "come_value_key",
     "field_type": WidgetsType.rangeWidget,
     "range": (1, 10, 1)
     },
    {"lbl": "Opt2", "target_key": "come_value_key_1",
     "field_type": WidgetsType.rangeWidget,
     "range": (1, 10, 1)
     },
]

DOVETAIL_BIT_PROFILES_CONFIGURATION = [
    {
        "lbl": "Bit #",  # this should be displaying as int, and with tag #, not mm
        "target_key": "bit_profile_number",
        "field_type": WidgetsType.rangeWidget,
        "range": machine_ranges.bit_profile_number,
        "unit": "#"
    },
    {
        "lbl": "Bit Angle",  # this should be displaying with unit deg, not mm
        "target_key": "bit_profile_angle",
        "field_type": WidgetsType.rangeWidget,
        "range": machine_ranges.bit_profile_angle,
        "unit": "Deg"
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
        "lbl": "Number of flutes",  # this should be displaying as in and with unit tag #, not mm
        "target_key": "bit_profile_number_of_flutes",
        "field_type": WidgetsType.rangeWidget,
        "range": machine_ranges.bit_profile_number_of_flutes,
        "unit": "#"
    },
    {
        "lbl": "Feed speed",
        "target_key": "bit_profile_feed_speed",
        "field_type": WidgetsType.speedWidget,
        "range": machine_ranges.bit_profile_feed_speed,
        "custom_lbl": {SpinUnitMode.MM_MODE: "mm/m", SpinUnitMode.IN_MODE: "IPM"}

    },
    {
        "lbl": "Spindle speed",
        "target_key": "bit_profile_spindle_speed",
        "field_type": WidgetsType.speedWidget,
        "range": machine_ranges.bit_profile_spindle_speed,
        "unit": "RPM"

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
    {
        "lbl": "Distance between Fences",
        "target_key": "dovetail_fence_distance",
        "field_type": WidgetsType.rangeWidget,
        "range": machine_ranges.dovetail_fence_distance
    },
    {
        "lbl": "spindle time out",
        "target_key": "spindle_time_out",
        "field_type": WidgetsType.speedWidget,
        "range": machine_ranges.spindle_time_out,
        "unit": "sec"
    },
]

# ************************* reset page *******************
DOVETAIL_RESET_PAGE_BUTTONS = \
    [
        {
            "lbl": "RESET CONTROLLER",
            "target_key": "reset_controller_btn",
        },
        {
            "lbl": "HOME",
            "target_key": "home_btn",
        },
        {
            "lbl": "GO TO PARK",
            "target_key": "go_to_park_btn",
        },
        {
            "lbl": "Measure Tool",
            "target_key": "measure_tool_btn",
        }
    ]

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
IMAGE_WIDTH = 640
IMAGE_HEIGHT = 480

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

# ***************************** E-Stop module ************************
IS_ESTOP_MODULE_ENABLED = False
ESTOP_MODULE_COM_PORT = "/dev/ttyACM0"
ESTOP_MODULE_BAUD_RATE = 4800
ESTOP_CHECK_STATUS_EVERY = 0.5  # check status every 0.5 sec

# ************************* grbl *********************
IS_GRBL_MODULE_ENABLED = True
GRBL_MODULE_COM_PORT = "/dev/ttyACM0"
