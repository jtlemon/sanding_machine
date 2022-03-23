import os, json, inspect
from apps.commons import SupportedMachines
from configurations.common_configurations import CURRENT_MACHINE

if CURRENT_MACHINE == SupportedMachines.dovetailMachine:
    file_name = "dovetail_configurations.json"
elif CURRENT_MACHINE == SupportedMachines.sandingMachine:
    file_name = "sanding_configurations.json"
else:
    raise ValueError("we only support dovetail only at the moment")

CONFIGURATION_FILE_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "custom_configurations", file_name)
if not os.path.isfile(CONFIGURATION_FILE_PATH):
    json.dump({}, open(CONFIGURATION_FILE_PATH, "w"))


class CustomMachineParamManager:
    __is_loaded = False

    @staticmethod
    def store():
        configuration_dict = dict()
        for key, value in inspect.getmembers(CustomMachineParamManager):
            if not key.startswith('_'):
                if not inspect.isfunction(value) and not inspect.ismethod(value):
                    configuration_dict[key] = value
        json.dump(configuration_dict, open(CONFIGURATION_FILE_PATH, "w"), indent=4)

    @staticmethod
    def load_configuration():
        json_content = json.load(open(CONFIGURATION_FILE_PATH))
        for key, value in json_content.items():
            setattr(CustomMachineParamManager, key, value)

    @staticmethod
    def set_value(key, value, auto_store=True):
        if CustomMachineParamManager.__is_loaded is False:
            CustomMachineParamManager.load_configuration()
            CustomMachineParamManager.__is_loaded = True
        setattr(CustomMachineParamManager, key, value)
        if auto_store:
            CustomMachineParamManager.store()

    @staticmethod
    def get_value(key, default=None):
        if CustomMachineParamManager.__is_loaded is False:
            CustomMachineParamManager.load_configuration()
            CustomMachineParamManager.__is_loaded = True
        return getattr(CustomMachineParamManager, key, default)

    @staticmethod
    def add_part_size(length, width):
        parts = getattr(CustomMachineParamManager, "part_sizes", [])
        if len(parts) > 100:
            parts.pop(0)
        parts.append((length, width))
        setattr(CustomMachineParamManager, "part_sizes", parts)
        CustomMachineParamManager.store()

    @staticmethod
    def get_avg_part_size():
        parts = getattr(CustomMachineParamManager, "part_sizes", [])
        avg_length, avg_width = 0, 0
        for length, width in parts:
            avg_length += length
            avg_width += width
        avg_length = avg_length/len(parts)
        avg_width = avg_width / len(parts)
        return  avg_length, avg_width
