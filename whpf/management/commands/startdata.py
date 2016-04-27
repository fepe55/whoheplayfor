# coding=utf-8
from django.core.management.base import BaseCommand

from whpf.helpers import get_players_api
from whpf.models import (Team, Player, Division, Conference, )
from whpf.teams import (ATLANTIC_TEAMS, CENTRAL_TEAMS, SOUTHEAST_TEAMS,
                        NORTHWEST_TEAMS, PACIFIC_TEAMS, SOUTHWEST_TEAMS)


class Command(BaseCommand):
    help = 'Creates conferences, divisions, teams and players'

    def handle(self, *args, **kwargs):

        # First, we create the conferences
        east = Conference.objects.create(name='East')
        west = Conference.objects.create(name='West')

        # Second, we create the divisions
        atlantic = Division.objects.create(name='Atlantic', conference=east)
        central = Division.objects.create(name='Central', conference=east)
        southeast = Division.objects.create(name='Southeast', conference=east)

        northwest = Division.objects.create(name='Northwest', conference=west)
        pacific = Division.objects.create(name='Pacific', conference=west)
        southwest = Division.objects.create(name='Southwest', conference=west)

        # Third, we create the teams
        nba_players = get_players_api()
        for p in nba_players:
            if p[7] and not Team.objects.filter(nba_id=p[7]).exists():
                if p[11] in ATLANTIC_TEAMS:
                    division = atlantic
                if p[11] in CENTRAL_TEAMS:
                    division = central
                if p[11] in SOUTHEAST_TEAMS:
                    division = southeast
                if p[11] in NORTHWEST_TEAMS:
                    division = northwest
                if p[11] in PACIFIC_TEAMS:
                    division = pacific
                if p[11] in SOUTHWEST_TEAMS:
                    division = southwest

                Team.objects.create(
                    nba_id=p[7],
                    city=p[8],
                    name=p[9],
                    abbreviation=p[10],
                    code=p[11],
                    division=division,
                )

        # And fourth, we create the teams
        # We loop twice on the nba_players for an easier code to read
        faceless = [204098, 1626162, 1626210]
        for p in nba_players:
            if p[3] != 0:
                team = Team.objects.get(nba_id=p[7])
                fl = p[0] in faceless
                Player.objects.create(
                    nba_id=p[0],
                    name=p[2],
                    team=team,
                    code=p[6],
                    faceless=fl,
                )
