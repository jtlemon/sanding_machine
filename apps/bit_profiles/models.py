from django.db import models
import jsonfield, json
from apps.commons import SupportedMachines

class BitProfile(models.Model):
    profile_name = models.CharField(max_length=20, default="")
    default_prams_json = jsonfield.JSONField()
    machine = models.IntegerField(choices=SupportedMachines.choices)

    def get_value(self, target_key):
        return self.default_prams_json.get(target_key, None)

    def get_decoded_json(self):
        return self.default_prams_json
    
    def set_value(self, key , value):
        self.default_prams_json[key] = value




