from django.db import models
import jsonfield, json
from apps.commons import SupportedMachines
from apps.bit_profiles.models import BitProfile



class DowelProfile(models.Model):
    profile_name = models.CharField(max_length=20, default="", unique=True)
    bit_profile = models.ForeignKey(BitProfile, on_delete=models.CASCADE)
    default_prams_json = jsonfield.JSONField()
    machine = models.IntegerField(choices=SupportedMachines.choices)

    def get_value(self, target_key):
        return self.default_prams_json.get(target_key, None)

    def get_decoded_json(self):
        return self.default_prams_json
    
    def set_value(self, key , value):
        self.default_prams_json[key] = value

class DowelJoint(models.Model):
    profile = models.ForeignKey(DowelProfile, on_delete=models.CASCADE)
    prams_json = jsonfield.JSONField()
    def get_value(self, target_key):
        return self.prams_json.get(target_key, None)

    def get_decoded_json(self):
        return self.prams_json
    
    def set_value(self, key , value):
        self.prams_json[key] = value



