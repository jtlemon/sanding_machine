from django.db import models


class SupportedMachines(models.IntegerChoices):
    dovetailMachine = 0
    drillDowelMachine = 1
