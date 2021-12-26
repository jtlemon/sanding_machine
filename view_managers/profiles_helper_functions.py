from configurations.constants_types import WidgetsType, AppSupportedOperations
from configurations import dovetail_configurations
from configurations import sanding_configuration
from configurations import common_configurations


def get_supported_profiles(profile_type):
    if profile_type == AppSupportedOperations.dowelsProfileOperation:
        ui_elements_descriptor = dovetail_configurations.DOVETAIL_DOWEL_JOINT_PROFILE_CONFIGURATION
    elif profile_type == AppSupportedOperations.jointProfilesOperation:
        ui_elements_descriptor = dovetail_configurations.DOVETAIL_JOINT_PROFILE_CONFIGURATION
    elif profile_type == AppSupportedOperations.bitProfilesOperation:
        ui_elements_descriptor = dovetail_configurations.DOVETAIL_BIT_PROFILES_CONFIGURATION
    elif profile_type == AppSupportedOperations.settingParametersOperation:
        if common_configurations.CURRENT_MACHINE == common_configurations.SupportedMachines.dovetailMachine:
            ui_elements_descriptor = dovetail_configurations.DOVETAIL_SETTING_CONFIGURATION
        elif common_configurations.CURRENT_MACHINE == common_configurations.SupportedMachines.sandingMachine:
            ui_elements_descriptor = sanding_configuration.SANDING_SETTING_CONFIGURATION
        else:
            raise ValueError("not supported machine....")
    elif profile_type == AppSupportedOperations.partProfileOperation:
        ui_elements_descriptor = sanding_configuration.SANDING_PART_PROFILE
    elif profile_type == AppSupportedOperations.individualSandPaperOperations:
        ui_elements_descriptor = sanding_configuration.SANDPAPER_PROFILE
    elif profile_type == AppSupportedOperations.doorStylesOperation:
        ui_elements_descriptor = sanding_configuration.SANDING_DOOR_STYLES_PROFILE
    else:
        raise ValueError(f"not implemented operation {profile_type}")

    return ui_elements_descriptor


def get_supported_profiles_meta(profile_type):
    supported_profiles = get_supported_profiles(profile_type)
    display_names = []
    target_keys = []
    default_values = []
    for profile in supported_profiles:
        display_names.append(profile.get("lbl"))
        target_keys.append(profile.get("target_key"))
        widget_type = profile.get("field_type", WidgetsType.rangeWidget)
        if widget_type == WidgetsType.rangeWidget or widget_type == widget_type.speedWidget or widget_type == widget_type.optionalRangeWidget:
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
    return display_names, target_keys, default_values
