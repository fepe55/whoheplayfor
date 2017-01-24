# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2017-01-24 19:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('whpf', '0006_player_being_updated'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='team',
            options={'ordering': ['division__conference__name', 'city', 'name']},
        ),
        migrations.AddField(
            model_name='player',
            name='times_guessed',
            field=models.IntegerField(default=0),
        ),
    ]
