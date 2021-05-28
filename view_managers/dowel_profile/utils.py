import configurations.static_app_configurations as static_configurations
from configurations.constants_types import WidgetsType


def get_supported_profiles():
    if static_configurations.CURRENT_MACHINE == static_configurations.SupportedMachines.dovetailMachine:
        supported_dowels_profiles = static_configurations.DOVETAIL_DOWEL_JOINT_PROFILE_CONFIGURATION
    else:
        raise ValueError("not supported machine.......")

    return supported_dowels_profiles


def get_supported_profiles_meta():
    supported_profiles = get_supported_profiles()
    display_names = []
    target_keys = []
    default_values = []
    for profile in supported_profiles:
        display_names.append(profile.get("lbl"))
        target_keys.append(profile.get("target_key"))
        widget_type = profile.get("field_type", WidgetsType.rangeWidget)
        if widget_type == WidgetsType.rangeWidget:
            widget_range = profile.get("range")
            default_values.append(widget_range[0])
        elif widget_type == WidgetsType.boolWidget:
            default_values.append(False)
        else:
            raise ValueError("not supported widget type (range/bool)")
    return  display_names, target_keys, default_values
