# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2017-02-16 21:09
from __future__ import unicode_literals

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('whpf', '0009_auto_20170125_1652'),
    ]

    operations = [
        migrations.CreateModel(
            name='Play',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('code', models.TextField()),
                ('score', models.IntegerField(default=0)),
                ('finished', models.BooleanField(default=False)),
                ('player', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PlaySetting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('value', models.CharField(max_length=255)),
                ('play', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='whpf.Play')),
            ],
        ),
    ]
