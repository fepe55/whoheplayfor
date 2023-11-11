# coding=utf-8
from django.core.management.base import BaseCommand

from whpf.helpers import get_players_api
from whpf.models import Player, Team

faceless = [204098, 1626162, 1626210]


class Command(BaseCommand):
    """Django Management command base class."""

    help = 'Creates players (DEPRECATED, use startdata)'

    def handle(self, *args, **kwargs):
        """Create players (DEPRECATED, use startdata)."""
        nba_players = get_players_api()
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
