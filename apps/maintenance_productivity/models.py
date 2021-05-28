from django.db import models


class Dowels(models.Model):
    no_of_dowel = models.IntegerField(default=0)
    date = models.DateField()


class Holes(models.Model):
    no_of_holes = models.IntegerField(default=0)
    date = models.DateField()


class Part(models.Model):
    part_size = models.FloatField(default=0)
    mode = models.CharField(max_length=20, default="")
    direction = models.CharField(max_length=20, default="")
    date = models.DateTimeField(auto_now=True)
    profile_name = models.CharField(max_length=50, default="", null=True)


class AxisMotion(models.Model):
    x_axis = models.FloatField(default=0)
    y_axis = models.FloatField(default=0)
    z_axis = models.FloatField(default=0)
    a_axis = models.FloatField(default=0)
    date = models.DateField()


class Maintainance(models.Model):
    date = models.DateField(auto_now=True)

