from __future__ import unicode_literals

import uuid

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse

from .managers import PlayerManager


class Options(models.Model):
    last_roster_update = models.DateTimeField()

    def __str__(self):
        return "Options"


class ModelWithDates(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Conference(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name}ern conference"

    def get_teams(self):
        teams = Team.objects.none()
        for division in self.divisions.all():
            teams |= division.teams.all()
        return teams


class Division(models.Model):
    name = models.CharField(max_length=255)
    conference = models.ForeignKey(Conference, related_name="divisions", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} division"


class Team(ModelWithDates):
    nba_id = models.IntegerField()
    city = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    abbreviation = models.CharField(max_length=255)
    code = models.CharField(max_length=255)
    division = models.ForeignKey(Division, related_name="teams", on_delete=models.CASCADE)
    times_guessed = models.IntegerField(default=0)
    times_guessed_right = models.IntegerField(default=0)
    times_guessed_wrong = models.IntegerField(default=0)
    times_guessed_pct = models.IntegerField(default=0)

    class Meta:
        ordering = ["division__conference__name", "city", "name"]

    def __str__(self):
        return f"{self.city} {self.name}"

    @property
    def times_guessed_wrong_pct(self):
        return 100 - self.times_guessed_pct

    @property
    def picture(self):
        # TEAM_PICTURE_URL = "http://stats.nba.com/media/img/teams/"\
        #     "logos/%s_logo.svg"
        # TEAM_PICTURE_URL = "https://i.cdn.turner.com/nba/nba/assets/logos/"\
        #     "teams/primary/web/%s.svg"
        TEAM_PICTURE_URL = "https://cdn.nba.com/logos/nba/{team_id}/global/D/logo.svg"
        return TEAM_PICTURE_URL.format(team_id=self.nba_id)

    def stats_url(self):
        return reverse(
            "whpf:stats_team",
            kwargs={
                "team_code": self.code,
            },
        )


class Player(ModelWithDates):
    active = models.BooleanField(default=True)
    being_updated = models.BooleanField(default=False)
    nba_id = models.IntegerField()
    name = models.CharField(max_length=255)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    code = models.CharField(max_length=255)
    faceless = models.BooleanField(default=False)
    times_guessed = models.IntegerField(default=0)
    times_guessed_right = models.IntegerField(default=0)
    times_guessed_wrong = models.IntegerField(default=0)
    times_guessed_pct = models.IntegerField(default=0)

    all_players = models.Manager()
    objects = PlayerManager()

    def __str__(self):
        return self.name

    @property
    def times_guessed_wrong_pct(self):
        return 100 - self.times_guessed_pct

    @property
    def picture(self):
        DEFAULT = (
            "https://i.cdn.turner.com/nba/nba/.element/img/2.0/sect/"
            "statscube/players/large/default_nba_headshot_v2.png"
        )
        # PLAYER_PICTURE_URL = "http://i.cdn.turner.com/nba/nba/.element/"\
        #     "img/2.0/sect/statscube/players/large/%s.png"
        # PLAYER_PICTURE_URL = "https://ak-static.cms.nba.com/wp-content/"\
        #     "uploads/headshots/nba/latest/260x190/%s.png"
        PLAYER_PICTURE_URL = "https://cdn.nba.com/headshots/nba/latest/260x190/{}.png"
        if self.faceless:
            return DEFAULT
        return PLAYER_PICTURE_URL.format(self.nba_id)


class Result(ModelWithDates):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.TextField()
    score = models.IntegerField(default=0)

    class Meta:
        ordering = ["-score"]

    def __str__(self):
        return self.code

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


class Play(ModelWithDates):
    player = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    code = models.TextField()
    score = models.IntegerField(default=0)
    finished = models.BooleanField(default=False)
    legacy = models.BooleanField(default=False)

    def __str__(self):
        return self.code


class PlaySetting(models.Model):
    name = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    play = models.ForeignKey(Play, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name}: {self.value}"
