from django.db import models
import jsonfield, json
from apps.commons import SupportedMachines
from apps.bit_profiles.models import BitProfile

class JoinProfile(models.Model):
    profile_name = models.CharField(max_length=20, default="")
    bit_profile = models.ForeignKey(BitProfile, on_delete=models.CASCADE)
    json_payload = jsonfield.JSONField()
    machine = models.IntegerField(choices=SupportedMachines.choices)

    
    def get_value(self, target_key):
        return self.json_payload.get(target_key, None)

    def get_decoded_json(self):
        return self.json_payload
    
    def set_value(self, key , value):
        self.json_payload[key] = value

