# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2017-01-24 20:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('whpf', '0007_auto_20170124_1440'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='times_guessed',
            field=models.IntegerField(default=0),
        ),
    ]
