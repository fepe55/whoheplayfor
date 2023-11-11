# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-23 18:33
from __future__ import unicode_literals

import datetime

from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('whpf', '0002_auto_20160423_1745'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='result',
            options={'ordering': ['-score']},
        ),
        migrations.AddField(
            model_name='result',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2016, 4, 23, 18, 33, 38, 173437, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='result',
            name='last_modified',
            field=models.DateTimeField(auto_now=True, default=datetime.datetime(2016, 4, 23, 18, 33, 42, 220974, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
