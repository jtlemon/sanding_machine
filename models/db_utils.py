from configurations.custom_pram_loader import CustomMachineParamManager
from apps.bit_profiles.models import BitProfile
from apps.joint_profiles.models import JoinProfile
from apps.dowel_profiles.models import DowelProfile
from view_managers.utils import display_error_message
from apps.sanding_machine import models as sandig_models

def get_current_program():
    program_name = CustomMachineParamManager.get_value("program_name", "")
    sanding_program = None
    try:
         sanding_program = sandig_models.SandingProgramPass.objects.get(sanding_program__name=program_name)
    except sandig_models.SandingProgramPass.DoesNotExist:
        pass
    return sanding_program


def get_current_door_style():
    door_style_name = CustomMachineParamManager.get_value("door_style", "")
    door_style = None
    try:
        door_style = sandig_models.DoorStyle.objects.get(profile_name=door_style_name)
    except sandig_models.DoorStyle.DoesNotExist:
        pass
    return door_style


def get_loaded_bit_profile():
    bit_id = CustomMachineParamManager.get_value("loaded_bit_id", -1)
    if bit_id == -1:
        bit_profile = None
    else:
        try:
            bit_profile = BitProfile.objects.get(pk=bit_id)
        except BitProfile.DoesNotExist:
            bit_profile = None
    return bit_profile


def get_loaded_joint_profile(get_first=False):
    if get_first:
        return JoinProfile.objects.first()
    else:
        joint_id = CustomMachineParamManager.get_value("loaded_joint_profile_id", -1)
        if joint_id == -1:
            joint_profile = None
        else:
            try:
                joint_profile = JoinProfile.objects.get(pk=joint_id)
            except JoinProfile.DoesNotExist:
                joint_profile = None
        return joint_profile


def get_loaded_dowel_profile(get_first=False):
    if get_first:
        return DowelProfile.objects.first()
    else:
        dowel_id = CustomMachineParamManager.get_value("loaded_dowel_profile_id", -1)
        if dowel_id == -1:
            dowel_profile = None
        else:
            try:
                dowel_profile = DowelProfile.objects.get(pk=dowel_id)
            except DowelProfile.DoesNotExist:
                dowel_profile = None
        return dowel_profile

    return DowelProfile.objects.first()


def is_joint_selected():
    return CustomMachineParamManager.get_value("loaded_profile_type", "") == "joint"


def is_dowel_selected():
    return CustomMachineParamManager.get_value("loaded_profile_type", "") == "dowel"

def is_bit_loaded():
    loaded_bit_id = CustomMachineParamManager.get_value("loaded_bit_id")
    if loaded_bit_id is None:
        CustomMachineParamManager.set_value("loaded_bit_id", -1, True)
        loaded_bit_id = -1
    return False if loaded_bit_id < 0 else True


def get_loaded_bit_name():
    loaded_bit_profile = get_loaded_bit_profile()
    loaded_bit_name = None
    if loaded_bit_profile is None:
        CustomMachineParamManager.set_value("loaded_bit_id", -1, True)
    else:
        loaded_bit_name = loaded_bit_profile.profile_name
    return loaded_bit_name


def bit_should_loaded_decorator(func):
    def wrapper_func(*args, **kwargs):
        if is_bit_loaded():
            func(*args, **kwargs)
        else:
            display_error_message("bit must loaded first")
    return wrapper_func








