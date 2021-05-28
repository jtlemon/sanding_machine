import json
import os

CONFIGURATION_FILE_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "main_system_configurations.json")


class MainConfigurationLoader:
    system_prams = json.load(open(CONFIGURATION_FILE_PATH))

    @staticmethod
    def get_spindle_speed_value():
        return MainConfigurationLoader.system_prams["general settings"]["spindle_speed"]

    @staticmethod
    def set_spindle_speed_value(new_value, auto_save=False):
        MainConfigurationLoader.system_prams["general settings"]["spindle_speed"] = new_value
        if auto_save:
            MainConfigurationLoader.save_configuration()

    @staticmethod
    def get_part_width_value():
        return MainConfigurationLoader.system_prams["general settings"]["part_width"]

    @staticmethod
    def set_part_width_value(new_value, auto_save=False):
        MainConfigurationLoader.system_prams["general settings"]["part_width"] = new_value
        if auto_save:
            MainConfigurationLoader.save_configuration()

    @staticmethod
    def get_feed_speed_value():
        return MainConfigurationLoader.system_prams["general settings"]["feed_speed"]

    @staticmethod
    def set_feed_speed_value(new_value, auto_save=False):
        MainConfigurationLoader.system_prams["general settings"]["feed_speed"] = new_value
        if auto_save:
            MainConfigurationLoader.save_configuration()

    @staticmethod
    def get_y_zero_value():
        return MainConfigurationLoader.system_prams["general settings"]["y_zero"]

    @staticmethod
    def set_y_zero_value(new_value, auto_save=False):
        MainConfigurationLoader.system_prams["general settings"]["y_zero"] = new_value
        if auto_save:
            MainConfigurationLoader.save_configuration()

    @staticmethod
    def get_z_zero_value():
        return MainConfigurationLoader.system_prams["general settings"]["z_zero"]

    @staticmethod
    def set_z_zero_value(new_value, auto_save=False):
        MainConfigurationLoader.system_prams["general settings"]["z_zero"] = new_value
        if auto_save:
            MainConfigurationLoader.save_configuration()

    @staticmethod
    def get_z_retract_distance_value():
        return MainConfigurationLoader.system_prams["general settings"]["z_retract_distance"]

    @staticmethod
    def set_z_retract_distance_value(new_value, auto_save=False):
        MainConfigurationLoader.system_prams["general settings"]["z_retract_distance"] = new_value
        if auto_save:
            MainConfigurationLoader.save_configuration()

    @staticmethod
    def get_hole_start_from_end_value():
        return MainConfigurationLoader.system_prams["general settings"]["hole_start_from_end"]

    @staticmethod
    def set_hole_start_from_end_value(new_value, auto_save=False):
        MainConfigurationLoader.system_prams["general settings"]["hole_start_from_end"] = new_value
        if auto_save:
            MainConfigurationLoader.save_configuration()

    @staticmethod
    def get_dowel_protrusion_offset_value():
        return MainConfigurationLoader.system_prams["general settings"]["dowel_protrusion_offset"]

    @staticmethod
    def set_dowel_protrusion_offset_value(new_value, auto_save=False):
        MainConfigurationLoader.system_prams["general settings"]["dowel_protrusion_offset"] = new_value
        if auto_save:
            MainConfigurationLoader.save_configuration()

    @staticmethod
    def get_drill_to_insert_offset_value():
        return MainConfigurationLoader.system_prams["general settings"]["drill_to_insert_offset"]

    @staticmethod
    def set_drill_to_insert_offset_value(new_value, auto_save=False):
        MainConfigurationLoader.system_prams["general settings"]["drill_to_insert_offset"] = new_value
        if auto_save:
            MainConfigurationLoader.save_configuration()

    @staticmethod
    def get_drill_to_insert_height_offset_value():
        return MainConfigurationLoader.system_prams["general settings"]["drill_to_insert_height_offset"]

    @staticmethod
    def set_drill_to_insert_height_offset_value(new_value, auto_save=False):
        MainConfigurationLoader.system_prams["general settings"]["drill_to_insert_height_offset"] = new_value
        if auto_save:
            MainConfigurationLoader.save_configuration()

    @staticmethod
    def get_water_injection_time_value():
        return MainConfigurationLoader.system_prams["general settings"]["water_injection_time"]

    @staticmethod
    def set_water_injection_time_value(new_value, auto_save=False):
        MainConfigurationLoader.system_prams["general settings"]["water_injection_time"] = new_value
        if auto_save:
            MainConfigurationLoader.save_configuration()

    @staticmethod
    def get_dowel_insertion_time_value():
        return MainConfigurationLoader.system_prams["general settings"]["dowel_insertion_time"]

    @staticmethod
    def set_dowel_insertion_time_value(new_value, auto_save=False):
        MainConfigurationLoader.system_prams["general settings"]["dowel_insertion_time"] = new_value
        if auto_save:
            MainConfigurationLoader.save_configuration()

    @staticmethod
    def get_dowel_insertion_delay_value():
        return MainConfigurationLoader.system_prams["general settings"]["dowel_insertion_delay"]

    @staticmethod
    def set_dowel_insertion_delay_value(new_value, auto_save=False):
        MainConfigurationLoader.system_prams["general settings"]["dowel_insertion_delay"] = new_value
        if auto_save:
            MainConfigurationLoader.save_configuration()

    @staticmethod
    def get_dowel_release_time_value():
        return MainConfigurationLoader.system_prams["general settings"]["dowel_release_time"]

    @staticmethod
    def set_dowel_release_time_value(new_value, auto_save=False):
        MainConfigurationLoader.system_prams["general settings"]["dowel_release_time"] = new_value
        if auto_save:
            MainConfigurationLoader.save_configuration()

    @staticmethod
    def get_distance_from_backedge_value():
        return MainConfigurationLoader.system_prams["general settings"]["distance_from_backedge"]

    @staticmethod
    def set_distance_from_backedge_value(new_value, auto_save=False):
        MainConfigurationLoader.system_prams["general settings"]["distance_from_backedge"] = new_value
        if auto_save:
            MainConfigurationLoader.save_configuration()

    @staticmethod
    def get_spindle_off_value():
        return MainConfigurationLoader.system_prams["general settings"]["spindle_off"]

    @staticmethod
    def set_spindle_off_value(new_value, auto_save=False):
        MainConfigurationLoader.system_prams["general settings"]["spindle_off"] = new_value
        if auto_save:
            MainConfigurationLoader.save_configuration()

    @staticmethod
    def get_min_weight_value():
        return MainConfigurationLoader.system_prams["general settings"]["min_weight"]

    @staticmethod
    def set_min_weight_value(new_value, auto_save=False):
        MainConfigurationLoader.system_prams["general settings"]["min_weight"] = new_value
        if auto_save:
            MainConfigurationLoader.save_configuration()

    @staticmethod
    def get_max_weight_value():
        return MainConfigurationLoader.system_prams["general settings"]["max_weight"]

    @staticmethod
    def set_max_weight_value(new_value, auto_save=False):
        MainConfigurationLoader.system_prams["general settings"]["max_weight"] = new_value
        if auto_save:
            MainConfigurationLoader.save_configuration()

    @staticmethod
    def get_left_xzero_value():
        return MainConfigurationLoader.system_prams["left settings"]["left_xzero"]

    @staticmethod
    def set_left_xzero_value(new_value, auto_save=False):
        MainConfigurationLoader.system_prams["left settings"]["left_xzero"] = new_value
        if auto_save:
            MainConfigurationLoader.save_configuration()

    @staticmethod
    def get_distance_between_fences_value():
        return MainConfigurationLoader.system_prams["right settings"]["distance_between_fences"]

    @staticmethod
    def set_distance_between_fences_value(new_value, auto_save=False):
        MainConfigurationLoader.system_prams["right settings"]["distance_between_fences"] = new_value
        if auto_save:
            MainConfigurationLoader.save_configuration()

    @staticmethod
    def get_left_active_value():
        return MainConfigurationLoader.system_prams["active side"]["left_active"]

    @staticmethod
    def set_left_active_value(new_value, auto_save=False):
        MainConfigurationLoader.system_prams["active side"]["left_active"] = new_value
        if auto_save:
            MainConfigurationLoader.save_configuration()

    @staticmethod
    def get_right_active_value():
        return MainConfigurationLoader.system_prams["active side"]["right_active"]

    @staticmethod
    def set_right_active_value(new_value, auto_save=False):
        MainConfigurationLoader.system_prams["active side"]["right_active"] = new_value
        if auto_save:
            MainConfigurationLoader.save_configuration()

    @staticmethod
    def get_time0_value():
        return MainConfigurationLoader.system_prams["active side"]["time0"]

    @staticmethod
    def get_time4_value():
        return MainConfigurationLoader.system_prams["active side"]["time4"]

    @staticmethod
    def get_time6_value():
        return MainConfigurationLoader.system_prams["active side"]["time6"]

    @staticmethod
    def get_time8_value():
        return MainConfigurationLoader.system_prams["active side"]["time8"]

    @staticmethod
    def get_time10_value():
        return MainConfigurationLoader.system_prams["active side"]["time10"]

    @staticmethod
    def get_base_time_value():
        return MainConfigurationLoader.system_prams["active side"]["base_time"]

    @staticmethod
    def set_base_time_value(new_value, auto_save=False):
        MainConfigurationLoader.system_prams["active side"]["base_time"] = new_value
        if auto_save:
            MainConfigurationLoader.save_configuration()

    @staticmethod
    def get_zip_code_value():
        return MainConfigurationLoader.system_prams["machine setup"]["zip_code"]

    @staticmethod
    def set_zip_code_value(new_value, auto_save=False):
        MainConfigurationLoader.system_prams["machine setup"]["zip_code"] = new_value
        if auto_save:
            MainConfigurationLoader.save_configuration()

    @staticmethod
    def get_bit_height_to_table_top_value():
        return MainConfigurationLoader.system_prams["machine setup"]["bit_height_to_table_top"]

    @staticmethod
    def set_bit_height_to_table_top_value(new_value, auto_save=False):
        MainConfigurationLoader.system_prams["machine setup"]["bit_height_to_table_top"] = new_value
        if auto_save:
            MainConfigurationLoader.save_configuration()

    @staticmethod
    def get_table_variations_readings():
        return MainConfigurationLoader.system_prams["table variations"]["readings"].copy()

    @staticmethod
    def get_time_format_value():
        return MainConfigurationLoader.system_prams["machine setup"].get("time_format", 24)

    @staticmethod
    def set_time_format_value(new_value, auto_save=False):
        MainConfigurationLoader.system_prams["machine setup"]["time_format"] = new_value
        if auto_save:
            MainConfigurationLoader.save_configuration()

    @staticmethod
    def get_last_dowel_mode_text():
        return MainConfigurationLoader.system_prams["machine setup"]["last_dowel_mode"]

    @staticmethod
    def set_last_dowel_mode_text(new_value, auto_save=False):
        MainConfigurationLoader.system_prams["machine setup"]["last_dowel_mode"] = new_value
        if auto_save:
            MainConfigurationLoader.save_configuration()

    @staticmethod
    def save_configuration():
        json.dump(MainConfigurationLoader.system_prams, open(CONFIGURATION_FILE_PATH, "w"), indent=4)
