# Generated by Django 3.1.1 on 2020-11-11 23:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maintenance_productivity', '0005_axismotion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='axismotion',
            name='date',
            field=models.DateField(auto_now=True),
        ),
    ]
