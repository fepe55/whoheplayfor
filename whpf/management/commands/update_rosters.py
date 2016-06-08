# coding=utf-8

from django.core.management.base import BaseCommand

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
        nba_players = get_players_api()
        for p in nba_players:
            player_qs = Player.objects.filter(nba_id)
            # If there is a player, we update it
            if player_qs.exists():
                # There SHOULD only be one
                player = player_qs.get()
            # If there isn't a player with that ID, we create it
            else:
                Crearlo

