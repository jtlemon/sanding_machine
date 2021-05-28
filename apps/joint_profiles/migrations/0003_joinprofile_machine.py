# Generated by Django 3.1.1 on 2021-05-28 21:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('joint_profiles', '0002_joinprofile_json_payload'),
    ]

    operations = [
        migrations.AddField(
            model_name='joinprofile',
            name='machine',
            field=models.IntegerField(choices=[(0, 'Dovetailmachine'), (1, 'Drilldowelmachine')], default=0),
        ),
    ]
