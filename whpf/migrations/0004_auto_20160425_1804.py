# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-25 18:04
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("whpf", "0003_auto_20160423_1833"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="team",
            options={"ordering": ["division__conference__name", "code"]},
        ),
    ]
