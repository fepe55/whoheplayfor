# -*- encoding: utf-8 -*-
from django import forms

TIME_CHOICES = [(0, 'Unlimited time'), (30, '30 seconds'),
                (60, '60 seconds'), (90, '90 seconds'), ]
ROUNDS_CHOICES = [(10, 10), (20, 20), (30, 30), ]
LIMIT_TEAMS_CHOICES = [
    ('all', 'All teams'),
    ('playoffs', 'Playoff teams'),
    ('west', 'West teams'),
    ('east', 'East teams'),
]


class GameForm(forms.Form):
    time = forms.ChoiceField(choices=TIME_CHOICES)
    rounds = forms.ChoiceField(choices=ROUNDS_CHOICES)
    limit_teams = forms.ChoiceField(choices=LIMIT_TEAMS_CHOICES)
    shuffle_teams = forms.BooleanField(required=False)
    show_player_name = forms.BooleanField(required=False)
