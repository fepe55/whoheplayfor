# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
import uuid

from django.db import models
from django.contrib.auth.models import User


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


class Division(models.Model):
    name = models.CharField(max_length=255)
    conference = models.ForeignKey(Conference, related_name="divisions")


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


class Player(ModelWithDates):
    active = models.BooleanField(default=True)
    nba_id = models.IntegerField()
    name = models.CharField(max_length=255)
    team = models.ForeignKey(Team)
    code = models.CharField(max_length=255)
    faceless = models.BooleanField(default=False)
    times_guessed_right = models.IntegerField(default=0)
    times_guessed_wrong = models.IntegerField(default=0)

    @property
    def picture(self):
        PLAYER_PICTURE_URL = "http://i.cdn.turner.com/nba/nba/.element/"\
            "img/2.0/sect/statscube/players/large/%s.png"
        return PLAYER_PICTURE_URL % self.code


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

    @property
    def difficulty(self):
        difficulty = 1
        if self.shuffle_teams:
            difficulty += 1
        if not self.show_player_name:
            difficulty += 1
        return difficulty

    def calculate_score(self):
        correct_guesses = 0
        wrong_guesses = 0
        difficulty = self.difficulty
        guesses = self.get_guesses()
        for guess in guesses:
            if guess['player'].team.id == guess['team'].id:
                correct_guesses += 1
            else:
                wrong_guesses += 1

        self.score = (3*correct_guesses - wrong_guesses) * difficulty
        self.save()
        return self.score

    def get_guesses(self):
        code = self.code
        code = code[1:]  # show_player_name
        code = code[1:]  # shuffle_teams
        code = code[3:]  # time_limit
        rounds = int(code[:3])
        code = code[3:]  # rounds
        guesses = []
        for i in xrange(rounds):
            guess_str = code[10*i:10*i+10]
            player_id = int(guess_str[:8])
            player = Player.objects.get(nba_id=player_id)
            team_id = int(guess_str[8:])
            team = Team.objects.get(nba_id__endswith=team_id)
            guess = {
                'round': i+1,
                'player': player,
                'team': team,
            }
            guesses.append(guess)
        return guesses

    class Meta:
        ordering = ['-score', ]
