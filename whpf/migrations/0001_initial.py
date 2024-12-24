# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-22 22:21
from __future__ import unicode_literals

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Conference",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="Division",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                (
                    "conference",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="divisions",
                        to="whpf.Conference",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Player",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_modified", models.DateTimeField(auto_now=True)),
                ("active", models.BooleanField(default=True)),
                ("nba_id", models.IntegerField()),
                ("name", models.CharField(max_length=255)),
                ("code", models.CharField(max_length=255)),
                ("faceless", models.BooleanField(default=False)),
                ("times_guessed_right", models.IntegerField(default=0)),
                ("times_guessed_wrong", models.IntegerField(default=0)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Result",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("code", models.TextField()),
                (
                    "time",
                    models.CharField(
                        choices=[
                            (0, b"Unlimited time"),
                            (30, b"30 seconds"),
                            (60, b"60 seconds"),
                            (90, b"90 seconds"),
                        ],
                        max_length=255,
                    ),
                ),
                (
                    "rounds",
                    models.CharField(choices=[(10, 10), (20, 20), (30, 30)], max_length=255),
                ),
                (
                    "limit_teams",
                    models.CharField(
                        choices=[
                            (b"all", b"All teams"),
                            (b"playoffs", b"Playoff teams"),
                            (b"west", b"West teams"),
                            (b"east", b"East teams"),
                        ],
                        max_length=255,
                    ),
                ),
                ("shuffle_teams", models.BooleanField()),
                ("show_player_name", models.BooleanField()),
                ("score", models.IntegerField(default=0)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Team",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_modified", models.DateTimeField(auto_now=True)),
                ("nba_id", models.IntegerField()),
                ("city", models.CharField(max_length=255)),
                ("name", models.CharField(max_length=255)),
                ("abbreviation", models.CharField(max_length=255)),
                ("code", models.CharField(max_length=255)),
                ("times_guessed_right", models.IntegerField(default=0)),
                ("times_guessed_wrong", models.IntegerField(default=0)),
                (
                    "division",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="teams",
                        to="whpf.Division",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="player",
            name="team",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="whpf.Team"),
        ),
    ]
