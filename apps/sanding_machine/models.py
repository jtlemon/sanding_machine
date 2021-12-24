from django.db import models
import jsonfield, json
from apps.commons import SupportedMachines


class PartProfile(models.Model):
    profile_name = models.CharField(max_length=20, default="", unique=True)
    json_payload = jsonfield.JSONField()
    machine = models.IntegerField(choices=SupportedMachines.choices)

    def get_value(self, target_key):
        return self.json_payload.get(target_key, None)

    def get_decoded_json(self):
        return self.json_payload

    def set_value(self, key, value):
        self.json_payload[key] = value


class Sandpaper(models.Model):
    profile_name = models.CharField(max_length=20, default="", unique=True)
    json_payload = jsonfield.JSONField()
    machine = models.IntegerField(choices=SupportedMachines.choices)

    def get_value(self, target_key):
        return self.json_payload.get(target_key, None)

    def get_decoded_json(self):
        return self.json_payload

    def set_value(self, key, value):
        self.json_payload[key] = value

    @staticmethod
    def get_sandpaper_names():
        return  [sandpaper.profile_name for sandpaper in Sandpaper.objects.all()]



class Sander(models.Model):
    name = models.CharField(max_length=50, unique=True)
    x_length = models.FloatField(default=0)
    y_length = models.FloatField(default=0)
    is_square = models.BooleanField(default=False)
    is_fine = models.BooleanField(default=False)
    installed_sandpaper = models.ForeignKey(Sandpaper, on_delete=models.CASCADE, default=None, null=True)



