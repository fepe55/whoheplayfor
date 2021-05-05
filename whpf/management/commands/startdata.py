# coding=utf-8
from django.core.management.base import BaseCommand

from whpf.helpers import get_players_api
from whpf.models import (Team, Player, Division, Conference, )
from whpf.teams import (
    ATLANTIC_TEAMS, CENTRAL_TEAMS, SOUTHEAST_TEAMS,
    NORTHWEST_TEAMS, PACIFIC_TEAMS, SOUTHWEST_TEAMS,
    TEAMS_ID,
)


class Command(BaseCommand):
    """Django Management command base class."""

    help = 'Creates conferences, divisions, teams and players'

    def handle(self, *args, **kwargs):
        """Create conferences, divisions, teams and players.
        Conferences, divisions are hardcoded.
        Teams id are hardcoded in whpf/teams.py, but they are validated with
        the API.
        Players come from the API.
        """

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
            # team_city = p['teamData']['city']
            # team_name = p['teamData']['nickname']
            # team_abbreviation = p['teamData']['tricode']
            # team_code = p['teamData']['urlName']
            if p[4] == 0:
                continue
            team_city = p[7]
            team_name = p[8]
            team_abbreviation = p[9]
            team_code = p[5]
            team_nba_id = TEAMS_ID[team_code]

            if not Team.objects.filter(nba_id=team_nba_id).exists():
                if team_code in ATLANTIC_TEAMS:
                    division = atlantic
                if team_code in CENTRAL_TEAMS:
                    division = central
                if team_code in SOUTHEAST_TEAMS:
                    division = southeast
                if team_code in NORTHWEST_TEAMS:
                    division = northwest
                if team_code in PACIFIC_TEAMS:
                    division = pacific
                if team_code in SOUTHWEST_TEAMS:
                    division = southwest

                Team.objects.create(
                    nba_id=team_nba_id,
                    city=team_city,
                    name=team_name,
                    abbreviation=team_abbreviation,
                    code=team_code,
                    division=division,
                )

        # And fourth, we create the teams
        # We loop twice on the nba_players for an easier code to read
        # faceless = [204098, 1626162, 1626210]
        faceless = []
        for p in nba_players:
            if p[4] == 0:
                continue

            team_code = p[5]
            team_nba_id = TEAMS_ID[team_code]

            nba_id = int(p[0])
            name = '{} {}'.format(p[2], p[1])
            code = name.replace(' ', '_').lower()

            team = Team.objects.get(nba_id=team_nba_id)
            fl = nba_id in faceless
            player_qs = Player.all_players.filter(nba_id=nba_id)
            if not player_qs.exists():
                Player.objects.create(
                    nba_id=nba_id,
                    name=name,
                    team=team,
                    code=code,
                    faceless=fl,
                )
