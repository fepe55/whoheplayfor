# coding=utf-8
import time
import requests

from django.utils import timezone
from django.core.management.base import BaseCommand

from whpf.models import (Player, Team, Options)
from whpf.helpers import get_players_api

"""
00 - "PERSON_ID",
01 - "DISPLAY_LAST_COMMA_FIRST",
02 - "DISPLAY_FIRST_LAST",
03 - "ROSTERSTATUS",
04 - "FROM_YEAR",
05 - "TO_YEAR",
06 - "PLAYERCODE",
07 - "TEAM_ID",
08 - "TEAM_CITY",
09 - "TEAM_NAME",
10 - "TEAM_ABBREVIATION",
11 - "TEAM_CODE",
12 - "GAMES_PLAYED_FLAG"
"""


class Command(BaseCommand):
    help = 'Updates players'

    def handle(self, *args, **kwargs):
        Player.all_players.update(active=False)
        nba_players = get_players_api()
        if not nba_players:
            print "Error with NBA.com"
            return
        for p in nba_players:
            # I'm guessing teams never change. if they do, all hell breaks
            # loose... or I just change a thing or two
            if not p[7]:
                continue
            team = Team.objects.get(nba_id=p[7])
            player_qs = Player.all_players.filter(nba_id=p[0])
            # If there is a player with that ID, we update it
            if player_qs.exists():
                # There SHOULD only be one.
                # player = player_qs.get()
                print "update", p[2]
                player_qs.update(
                    name=p[2],
                    team=team,
                    code=p[6],
                    active=True,
                )

            # If there isn't a player with that ID, we create it
            else:
                Player.all_players.create(
                    nba_id=p[0],
                    name=p[2],
                    team=team,
                    code=p[6],
                    active=True,
                )
                print "create", p[2]

        # Lastly, we find the faceless-ones

        for p in Player.all_players.all():
            r = requests.get(p.picture)
            if r.status_code == 200:
                p.faceless = False
                p.save()
                print p, 'has a face!'
            elif r.status_code == 404:
                print p, 'has no face ------------------------------'
                p.faceless = True
                p.save()
            else:
                print 'error with', p, '++++++++++++++++++++++++++++'

            # Sleep to avoid a possible anti-throttling from the server
            time.sleep(2)

        # And we update the last_roster_update date
        options = Options.objects.all()
        if options.exists():
            options = options.get()
        else:
            options = Options()
        options.last_roster_update = timezone.now()
        options.save()
