import configurations.static_app_configurations as static_configurations

from configurations.constants_types import WidgetsType


def get_supported_profiles(profile_type):
    if static_configurations.CURRENT_MACHINE == static_configurations.SupportedMachines.dovetailMachine:
        if profile_type == static_configurations.AppSupportedOperations.dowelsProfileOperation:
              supported_dowels_profiles = static_configurations.DOVETAIL_DOWEL_JOINT_PROFILE_CONFIGURATION
        elif profile_type == static_configurations.AppSupportedOperations.jointProfilesOperation:
              supported_dowels_profiles = static_configurations.DOVETAIL_JOINT_PROFILE_CONFIGURATION
        elif profile_type == static_configurations.AppSupportedOperations.bitProfilesOperation:
            supported_dowels_profiles = static_configurations.DOVETAIL_BIT_PROFILES_CONFIGURATION
        elif profile_type == static_configurations.AppSupportedOperations.settingParametersOperation:
            supported_dowels_profiles = static_configurations.DOVETAIL_SETTING_CONFIGURATION
        else:
            raise ValueError(f"not implemented operation {profile_type}")

    else:
        raise ValueError("not supported machine.......")

    return supported_dowels_profiles


def get_supported_profiles_meta(profile_type):
    supported_profiles = get_supported_profiles(profile_type)
    display_names = []
    target_keys = []
    default_values = []
    for profile in supported_profiles:
        display_names.append(profile.get("lbl"))
        target_keys.append(profile.get("target_key"))
        widget_type = profile.get("field_type", WidgetsType.rangeWidget)
        if widget_type == WidgetsType.rangeWidget or widget_type == widget_type.speedWidget:
            widget_range = profile.get("range")
            default_values.append(widget_range[0])
        elif widget_type == WidgetsType.boolWidget:
            default_values.append(False)
        elif widget_type == WidgetsType.textWidget:
            default_values.append("")
        elif widget_type == WidgetsType.optionWidget:
            options = profile.get("options")
            default_values.append(options[0])
        else:
            raise ValueError("not supported widget type (range/bool)")
    return  display_names, target_keys, default_values