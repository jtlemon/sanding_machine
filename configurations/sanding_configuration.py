from . import machine_ranges
from .constants_types import AppSupportedOperations, WidgetsType

SUPPORTED_SANDING_OPERATIONS = [
    AppSupportedOperations.sandingCameraOperations,
    AppSupportedOperations.doorStylesOperation,
    AppSupportedOperations.sandingProgramsOperations,
    AppSupportedOperations.sandersManagementOperations,
    AppSupportedOperations.individualSandPaperOperations,
    AppSupportedOperations.restMachineOperation,
    AppSupportedOperations.settingParametersOperation,

]

SANDING_DOOR_STYLES_PROFILE = [
    {
        "lbl": "Outside edge width",
        "target_key": "outside_edge_width",
        "field_type": WidgetsType.rangeWidget,
        "range": machine_ranges.door_styles_outside_edge_width,
        "tooltip": ""
    },
    {
        "lbl": "Inside Edge Width",
        "target_key": "inside_edge_width",
        "field_type": WidgetsType.rangeWidget,
        "range": machine_ranges.door_styles_inside_edge_width
    },
    {
        "lbl": "Frame Width",
        "target_key": "frame_width",
        "field_type": WidgetsType.rangeWidget,
        "range": machine_ranges.door_styles_frame_width
    },
    {
        "lbl": "HBFIE",
        "target_key": "hold_back_inside_edge",
        "field_type": WidgetsType.rangeWidget,
        "range": machine_ranges.door_styles_hold_back_from_edges
    },
    {
        "lbl": "Total Profile Width",
        "target_key": "total_profile_width",
        "field_type": WidgetsType.calculatedValue,
    }
]

SANDING_PART_PROFILE = [
    {
        "lbl": "Stile Width",  # this should be displaying with unit deg, not mm
        "target_key": "part_stile_width",
        "field_type": WidgetsType.rangeWidget,
        "range": machine_ranges.part_stile_width,
    },
    {
        "lbl": "Width",  # this should be displaying with unit deg, not mm
        "target_key": "part_profile_width",
        "field_type": WidgetsType.optionalRangeWidget,
        "range": machine_ranges.part_profile_width,
    },
    {
        "lbl": "Panel Width",  # this should be displaying with unit deg, not mm
        "target_key": "part_profile_panel_width",
        "field_type": WidgetsType.optionalRangeWidget,
        "range": machine_ranges.part_profile_panel_width,
    },
]

SANDPAPER_PROFILE = [
    {
        "lbl": "GRIT",  # this should be displaying with unit deg, not mm
        "target_key": "sanding_grit",
        "field_type": WidgetsType.rangeWidget,
        "range": machine_ranges.sanding_grit_range,
        "precession": 0,
        "unit": "#"
    },
    {
        "lbl": "Pressure",  # this should be displaying with unit deg, not mm
        "target_key": "sanding_pressure",
        "field_type": WidgetsType.rangeWidget,
        "range": machine_ranges.sanding_pressure,
        "precession": 0,
        "unit": " "
    },
    {
        "lbl": "HBFE",  # hold back from edge
        "target_key": "sanding_hold_back_from_edges",
        "field_type": WidgetsType.rangeWidget,
        "range": machine_ranges.sanding_hold_back_from_edges,
        "precession": 1
    },
    {
        "lbl": "overhang",  # this should be displaying with unit deg, not mm
        "target_key": "sandpaper_overhang",
        "field_type": WidgetsType.rangeWidget,
        "range": machine_ranges.sandpaper_overhang,
        "precession": 0,
        "unit": "%"
    },
    {
        "lbl": "Overlap",  # this should be displaying with unit deg, not mm
        "target_key": "sandpaper_overlap",
        "field_type": WidgetsType.rangeWidget,
        "range": machine_ranges.sandpaper_Overlap,
        "precession": 0,
        "unit": "%"
    },
    {
        "lbl": "Speed",
        "target_key": "sandpaper_speed",
        "field_type": WidgetsType.speedWidget,
        "range": machine_ranges.sandpaper_speed,
        "unit": "%"
    },

]
SANDING_SETTING_CONFIGURATION = [
    {
        "lbl": "X zero",
        "target_key": "machine_x_zero",
        "field_type": WidgetsType.rangeWidget,
        "range": machine_ranges.sander_x_zero
    },
    {
        "lbl": "S1 X",
        "target_key": "sander1_x_value",
        "field_type": WidgetsType.rangeWidget,
        "range": machine_ranges.dovetail_setting_x_zero
    },

    {
        "lbl": "S2 X",
        "target_key": "sander2_x_value",
        "field_type": WidgetsType.rangeWidget,
        "range": machine_ranges.dovetail_setting_x_zero
    },

    {
        "lbl": "S3 X",
        "target_key": "sander3_x_value",
        "field_type": WidgetsType.rangeWidget,
        "range": machine_ranges.dovetail_setting_x_zero
    },

    {
        "lbl": "S4 X",
        "target_key": "sander4_x_value",
        "field_type": WidgetsType.rangeWidget,
        "range": machine_ranges.dovetail_setting_x_zero
    },
    {
        "lbl": "Y zero",
        "target_key": "machine_y_zero",
        "field_type": WidgetsType.rangeWidget,
        "range": machine_ranges.dovetail_setting_x_zero
    },
    {
        "lbl": "S1 Y",
        "target_key": "sander1_y_value",
        "field_type": WidgetsType.rangeWidget,
        "range": machine_ranges.dovetail_setting_y_zero
    },
    {
        "lbl": "S2 Y",
        "target_key": "sander2_y_value",
        "field_type": WidgetsType.rangeWidget,
        "range": machine_ranges.dovetail_setting_y_zero
    },

    {
        "lbl": "S3 Y",
        "target_key": "sander3_y_value",
        "field_type": WidgetsType.rangeWidget,
        "range": machine_ranges.dovetail_setting_y_zero
    },
    {
        "lbl": "S4 Y",
        "target_key": "sander4_y_value",
        "field_type": WidgetsType.rangeWidget,
        "range": machine_ranges.dovetail_setting_y_zero
    },

]
SANDING_RESET_PAGE_BUTTONS = [
    {
        "lbl": "RESET CONTROLLER",
        "target_key": "reset_controller_btn"
    },
    {
        "lbl": "HOME",
        "target_key": "home_btn"
    },
    {
        "lbl": "GO TO PARK",
        "target_key": "go_to_park_btn"
    },
]
