from django.db import models
import jsonfield, json

class JoinProfile(models.Model):
    profile_name = models.CharField(max_length=20, default="")
    json_payload = jsonfield.JSONField()
    
    def get_value(self, target_key):
        return self.json_payload.get(target_key, None)

    def get_decoded_json(self):
        return self.json_payload
    
    def set_value(self, key , value):
        self.json_payload[key] = value

