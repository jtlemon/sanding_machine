from configurations.custom_pram_loader import CustomMachineParamManager
from apps.bit_profiles.models import BitProfile
from apps.joint_profiles.models import JoinProfile
from apps.dowel_profiles.models import DowelProfile


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


def get_loaded_joint_profile():
    return JoinProfile.objects.first()


def get_loaded_dowel_profile():
    return DowelProfile.objects.first()
