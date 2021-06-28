from configurations.custom_pram_loader import CustomMachineParamManager
from apps.bit_profiles.models import BitProfile


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

