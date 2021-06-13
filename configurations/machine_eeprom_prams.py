import os, json
CONFIGURATION_FILE_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "machine_prams.json")


class MachineEepromPrams:
    __is_loaded = False
    @staticmethod
    def load_configuration():
        json_content = json.load(open(CONFIGURATION_FILE_PATH))
        for key, value in json_content.items():
            setattr(MachineEepromPrams, key, value)


    @staticmethod
    def get_value(key, default=None):
        if MachineEepromPrams.__is_loaded is False:
            MachineEepromPrams.load_configuration()
            MachineEepromPrams.__is_loaded = True
        return getattr(MachineEepromPrams, key, default)
