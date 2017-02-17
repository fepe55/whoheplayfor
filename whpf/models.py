# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
import uuid

from django.db import models
from django.contrib.auth.models import User

from .managers import PlayerManager


class Options(models.Model):
    last_roster_update = models.DateTimeField()


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
    times_guessed = models.IntegerField(default=0)
    times_guessed_right = models.IntegerField(default=0)
    times_guessed_wrong = models.IntegerField(default=0)
    times_guessed_pct = models.IntegerField(default=0)

    @property
    def times_guessed_wrong_pct(self):
        return 100 - self.times_guessed_pct

    @property
    def picture(self):
        # TEAM_PICTURE_URL = "http://stats.nba.com/media/img/teams/"\
        #     "logos/%s_logo.svg"
        TEAM_PICTURE_URL = "https://i.cdn.turner.com/nba/nba/assets/logos/"\
            "teams/primary/web/%s.svg"
        return TEAM_PICTURE_URL % self.abbreviation

    def __unicode__(self):
        return "%s %s" % (self.city, self.name, )

    class Meta:
        ordering = ['division__conference__name', 'city', 'name', ]


class Player(ModelWithDates):
    active = models.BooleanField(default=True)
    being_updated = models.BooleanField(default=False)
    nba_id = models.IntegerField()
    name = models.CharField(max_length=255)
    team = models.ForeignKey(Team)
    code = models.CharField(max_length=255)
    faceless = models.BooleanField(default=False)
    times_guessed = models.IntegerField(default=0)
    times_guessed_right = models.IntegerField(default=0)
    times_guessed_wrong = models.IntegerField(default=0)
    times_guessed_pct = models.IntegerField(default=0)

    all_players = models.Manager()
    objects = PlayerManager()

    @property
    def times_guessed_wrong_pct(self):
        return 100 - self.times_guessed_pct

    @property
    def picture(self):
        DEFAULT = "https://i.cdn.turner.com/nba/nba/.element/img/2.0/sect/"\
            "statscube/players/large/default_nba_headshot_v2.png"
        # PLAYER_PICTURE_URL = "http://i.cdn.turner.com/nba/nba/.element/"\
        #     "img/2.0/sect/statscube/players/large/%s.png"
        PLAYER_PICTURE_URL = "https://ak-static.cms.nba.com/wp-content/"\
            "uploads/headshots/nba/latest/260x190/%s.png"
        if self.faceless:
            return DEFAULT
        return PLAYER_PICTURE_URL % str(self.nba_id)

    def __unicode__(self):
        return "%s" % (self.name, )


class Result(ModelWithDates):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User)
    code = models.TextField()
    score = models.IntegerField(default=0)

    # @property
    # def show_player_name(self):
    #     return self.code[:1] == '1'

    # @property
    # def shuffle_teams(self):
    #     return self.code[1:2] == '1'

    # @property
    # def time(self):
    #     return int(self.code[2:5])

    # @property
    # def rounds(self):
    #     return int(self.code[5:8])

    @property
    def parsed_code(self):
        from .helpers import parse_code
        return parse_code(self.code)

    def calculate_score(self):
        from .helpers import get_score
        self.score = get_score(self.code)
        self.save()
        return self.score

    class Meta:
        ordering = ['-score', ]


class Play(ModelWithDates):
    player = models.ForeignKey(User, blank=True, null=True)
    code = models.TextField()
    score = models.IntegerField(default=0)
    finished = models.BooleanField(default=False)
    legacy = models.BooleanField(default=False)


class PlaySetting(models.Model):
    name = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    play = models.ForeignKey(Play)
