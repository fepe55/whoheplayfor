# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
import uuid

from django.db import models
from django.contrib.auth.models import User

from .managers import PlayerManager


class ModelWithDates(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Conference(models.Model):
    name = models.CharField(max_length=255)

    def get_teams(self):
        teams = Team.objects.None()
        for division in self.divisions.all():
            teams |= division.teams.all()
        return teams

    def __unicode__(self):
        return "%sern conference" % (self.name, )


class Division(models.Model):
    name = models.CharField(max_length=255)
    conference = models.ForeignKey(Conference, related_name="divisions")

    def __unicode__(self):
        return "%s division" % (self.name, )


class Team(ModelWithDates):
    nba_id = models.IntegerField()
    city = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    abbreviation = models.CharField(max_length=255)
    code = models.CharField(max_length=255)
    division = models.ForeignKey(Division, related_name="teams")
    times_guessed_right = models.IntegerField(default=0)
    times_guessed_wrong = models.IntegerField(default=0)

    @property
    def picture(self):
        TEAM_PICTURE_URL = "http://stats.nba.com/media/img/teams/"\
            "logos/%s_logo.svg"
        return TEAM_PICTURE_URL % self.abbreviation

    def __unicode__(self):
        return "%s %s" % (self.city, self.name, )

    class Meta:
        ordering = ['division__conference__name', 'code', ]


class Player(ModelWithDates):
    active = models.BooleanField(default=True)
    nba_id = models.IntegerField()
    name = models.CharField(max_length=255)
    team = models.ForeignKey(Team)
    code = models.CharField(max_length=255)
    faceless = models.BooleanField(default=False)
    times_guessed_right = models.IntegerField(default=0)
    times_guessed_wrong = models.IntegerField(default=0)

    objects = PlayerManager()

    @property
    def picture(self):
        PLAYER_PICTURE_URL = "http://i.cdn.turner.com/nba/nba/.element/"\
            "img/2.0/sect/statscube/players/large/%s.png"
        return PLAYER_PICTURE_URL % self.code

    def __unicode__(self):
        return "%s" % (self.name, )


class Result(ModelWithDates):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User)
    code = models.TextField()
    score = models.IntegerField(default=0)

    @property
    def show_player_name(self):
        return self.code[:1] == '1'

    @property
    def shuffle_teams(self):
        return self.code[1:2] == '1'

    @property
    def time(self):
        return int(self.code[2:5])

    @property
    def rounds(self):
        return int(self.code[5:8])

    def calculate_score(self):
        from .helpers import get_score
        self.score = get_score(self.code)
        self.save()
        return self.score

    class Meta:
        ordering = ['-score', ]
