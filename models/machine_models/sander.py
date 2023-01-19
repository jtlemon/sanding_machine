import os

try:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    from django.core.wsgi import get_wsgi_application

    application = get_wsgi_application()
except Exception as e:
    print(e)

from apps.sanding_machine import models
from configurations.custom_pram_loader import CustomMachineParamManager
from models.machine_models.generate_config import  sander_dictionary, sander_on_delay, sander_off_delay
class SanderControl:
    def __init__(self, sander_db_obj: models.Sander):
        self._active_sander_id = sander_db_obj.pk
        self._sander_db_obj = sander_db_obj

    def on(self, pressure):
        if self._active_sander_id not in sander_dictionary:
            raise Exception("Sander ID is invalid")
        # put the logic

        x_sander = self._sander_db_obj.x_length

        return f'{sander_dictionary[self._active_sander_id]["extend"]}(extend)' "\n" \
               f'g4p{sander_on_delay}(delay for sander to extend)' "\n" \
               f'{sander_dictionary[self._active_sander_id]["on"]}m3s{pressure}(turn on sander and set pressure)' "\n" \
               f'g4p{sander_on_delay}(delay for sander to start)' "\n"

    def off(self):
        if self._active_sander_id not in sander_dictionary:
            raise Exception("Sander ID is invalid")

        return f'{sander_dictionary[self._active_sander_id]["retract"]}'"\n" \
               f'{sander_dictionary[self._active_sander_id]["off"]}' \
               's1000'"\n" \
               f'g4p{sander_off_delay}(delay for retraction)'"\n" \
               'm5(cancel pressure control)'"\n"

    def get_x_value(self):
        return self._sander_db_obj.x_length

    def get_y_value(self):
        return self._sander_db_obj.y_length

    def get_offset(self):
        return sander_dictionary[self._active_sander_id]['offset']

    def get_work_plane(self):
        return 'g18 g21 (workplane selection)'

    def map_pressure(self, x):
        in_min = 0
        in_max = 100
        out_min = CustomMachineParamManager.get_value("min_pressure")
        out_max = CustomMachineParamManager.get_value("max_pressure")
        shifted = int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)
        shifted2 = int((shifted - 0) * (100 - 0) / (30 - 0) + 0)
        return shifted2