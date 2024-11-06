# coding=utf-8
from django.core.management.base import BaseCommand

from whpf.helpers import start_data


class Command(BaseCommand):
    """Django Management command base class."""

    help = "Creates conferences, divisions, teams and players"

    def handle(self, *args, **kwargs):
        """Create conferences, divisions, teams and players.
        Conferences, divisions are hardcoded.
        Teams id are hardcoded in whpf/teams.py, but they are validated with
        the API.
        Players come from the API.
        """
        start_data()
