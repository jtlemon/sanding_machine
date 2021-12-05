# Generated by Django 3.1.1 on 2021-12-03 17:06

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('sanding_machine', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sandpaper',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sand_paper_number', models.CharField(default='', max_length=20, unique=True)),
                ('json_payload', jsonfield.fields.JSONField(default=dict)),
                ('machine', models.IntegerField(choices=[(0, 'Dovetailmachine'), (1, 'Drilldowelmachine')])),
            ],
        ),
    ]
