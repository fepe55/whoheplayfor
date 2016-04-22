# coding=utf-8
from django.core.management.base import BaseCommand
from whpf.views import get_players
from whpf.models import (Team, Division, )
from whpf.teams import (ATLANTIC_TEAMS, CENTRAL_TEAMS, SOUTHEAST_TEAMS,
                        NORTHWEST_TEAMS, PACIFIC_TEAMS, SOUTHWEST_TEAMS)


class Command(BaseCommand):
    help = 'Create teams'

    def handle(self, *args, **kwargs):
        nba_players = get_players()
        for p in nba_players:
            if not Team.objects.filter(nba_id=p[7]).exists():
                if p[11] in ATLANTIC_TEAMS:
                    division = Division.objects.get(name='Atlantic')
                if p[11] in CENTRAL_TEAMS:
                    division = Division.objects.get(name='Central')
                if p[11] in SOUTHEAST_TEAMS:
                    division = Division.objects.get(name='Southeast')
                if p[11] in NORTHWEST_TEAMS:
                    division = Division.objects.get(name='Northwest')
                if p[11] in PACIFIC_TEAMS:
                    division = Division.objects.get(name='Pacific')
                if p[11] in SOUTHWEST_TEAMS:
                    division = Division.objects.get(name='Southwest')

                Team.objects.create(
                    nba_id=p[7],
                    city=p[8],
                    name=p[9],
                    abbreviation=p[10],
                    code=p[11],
                    division=division,
                )
