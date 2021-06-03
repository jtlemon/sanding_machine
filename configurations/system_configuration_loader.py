import json, os, inspect

CONFIGURATION_FILE_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "generic_configurations.json")


class MainConfigurationLoader:
    __is_loaded = False
    @staticmethod
    def store():
        configuration_dict = dict()
        for key, value in inspect.getmembers(MainConfigurationLoader):
            if not key.startswith('_'):
                if not inspect.isfunction(value) and not inspect.ismethod(value):
                    configuration_dict[key] = value
        json.dump(configuration_dict, open(CONFIGURATION_FILE_PATH, "w"), indent=4)

    @staticmethod
    def load_configuration():
        json_content = json.load(open(CONFIGURATION_FILE_PATH))
        for key, value in json_content.items():
            setattr(MainConfigurationLoader, key, value)

    @staticmethod
    def set_value(key, value, auto_store=True):
        if MainConfigurationLoader.__is_loaded is False:
            MainConfigurationLoader.load_configuration()
            MainConfigurationLoader.__is_loaded = True
        setattr(MainConfigurationLoader, key, value)
        if auto_store:
            MainConfigurationLoader.store()

    @staticmethod
    def get_value(key, default=None):
        if MainConfigurationLoader.__is_loaded is False:
            MainConfigurationLoader.load_configuration()
            MainConfigurationLoader.__is_loaded = True
        return getattr(MainConfigurationLoader, key, default)


