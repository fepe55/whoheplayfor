# coding=utf-8
import time
import requests
from sys import stdout

from django.utils import timezone
from django.core.management.base import BaseCommand

from whpf.models import (Player, Team, Options)
from whpf.helpers import get_players_api

#  00 - "PERSON_ID"
#  01 - "PLAYER_LAST_NAME"
#  02 - "PLAYER_FIRST_NAME"
#  03 - "PLAYER_SLUG"
#  04 - "TEAM_ID"
#  05 - "TEAM_SLUG"
#  06 - "IS_DEFUNCT"
#  07 - "TEAM_CITY"
#  08 - "TEAM_NAME"
#  09 - "TEAM_ABBREVIATION"
#  10 - "JERSEY_NUMBER"
#  11 - "POSITION"
#  12 - "HEIGHT"
#  13 - "WEIGHT"
#  14 - "COLLEGE"
#  15 - "COUNTRY"
#  16 - "DRAFT_YEAR"
#  17 - "DRAFT_ROUND"
#  18 - "DRAFT_NUMBER"
#  19 - "ROSTER_STATUS"
#  20 - "FROM_YEAR"
#  21 - "TO_YEAR"
#  22 - "PTS"
#  23 - "REB"
#  24 - "AST"
#  25 - "STATS_TIMEFRAME"


class Command(BaseCommand):
    """Django Management command base class."""

    help = 'Updates players'

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-faceless-check',
            action='store_true',
            help='Don\'t check faces URLs',
        )

    def handle(self, *args, **options):
        """Update players database using data from API.
        Check if the player's generated face URL exists.
        """
        no_faceless_check = options['no_faceless_check']

        # Player.all_players.update(active=False)
        start_time = timezone.now()

        self.stdout.write('Starting at {}'.format(start_time))
        self.stdout.write('Getting all the players from the API... ')
        stdout.flush()
        nba_players = get_players_api()
        self.stdout.write('DONE')
        self.stdout.write('Marking all players as being updated... ')
        stdout.flush()
        if not nba_players:
            self.stdout.write("Error with NBA.com")
            return
        # We mark every player as being_updated and active true (for cases
        # where a player was inactive, then became active)
        Player.all_players.update(being_updated=True, active=True)
        self.stdout.write('DONE')
        # for p in nba_players:
        #     # I'm guessing teams never change. if they do, all hell breaks
        #     # loose... or I just change a thing or two
        #     if not p[7]:
        #         continue
        #     team = Team.objects.get(nba_id=p[7])
        #     player_qs = Player.all_players.filter(nba_id=p[0])
        #     # If there is a player with that ID, we update it
        #     if player_qs.exists():
        #         # There SHOULD only be one.
        #         # player = player_qs.get()
        #         print "update", p[2]
        #         player_qs.update(
        #             name=p[2],
        #             team=team,
        #             code=p[6],
        #             being_updated=False,
        #         )

        #     # If there isn't a player with that ID, we create it
        #     else:
        #         Player.all_players.create(
        #             nba_id=p[0],
        #             name=p[2],
        #             team=team,
        #             code=p[6],
        #             being_updated=False,
        #         )
        #         print "create", p[2]

        for p in nba_players:
            # I'm guessing teams never change. if they do, all hell breaks
            # loose... or I just change a thing or two
            # IF NOT TEAM?
            if p[4] == 0:
                continue
            team_code = p[5]
            team = Team.objects.get(code=team_code)
            nba_id = int(p[0])
            name = '{} {}'.format(p[2], p[1])
            code = name.replace(' ', '_').lower()
            player_qs = Player.all_players.filter(nba_id=nba_id)
            # If there is a player with that ID, we update it
            if player_qs.exists():
                # There SHOULD only be one.
                # player = player_qs.get()
                self.stdout.write('updating {}'.format(name))

                player_qs.update(
                    name=name,
                    team=team,
                    code=code,
                    being_updated=False,
                )

            # If there isn't a player with that ID, we create it
            else:
                Player.all_players.create(
                    nba_id=nba_id,
                    name=name,
                    team=team,
                    code=code,
                    being_updated=False,
                )
                self.stdout.write('created {}'.format(name))

        # If your being_updated flag wasn't changed to False, it means you
        # weren't modified or added, so you disappeared. We set you as
        # inactive
        Player.all_players.filter(being_updated=True).update(
            being_updated=False, active=False
        )

        # Lastly, we find the faceless-ones
        errors = []
        faceless = []

        if not no_faceless_check:
            active_players = Player.all_players.filter(
                active=True
            ).order_by('name')
            current = 1
            for p in active_players:
                self.stdout.write(f'[{current}/{active_players.count()}]')
                current += 1
                try:
                    r = requests.get(p.picture)
                    if r.status_code == 200:
                        p.faceless = False
                        p.save()
                        self.stdout.write(f'{p} ({p.id}) has a face')
                    elif r.status_code == 404:
                        self.stdout.write(
                            f'{p} ({p.id}) has no face --------------------'
                        )
                        faceless.append(p)
                        p.faceless = True
                        p.save()
                    else:
                        self.stdout.write(f'error with {p} ({p.id}) (Error code: {r.status_code}) ++++++')  # noqa: E501
                        p.faceless = True
                        p.save()
                        errors.append({'player': p, 'error': r.status_code})

                except requests.exceptions.RequestException as e:
                    self.stdout.write(str(e))
                    errors.append({'player': p, 'error': e})

                # Sleep to avoid a possible throttling or ban from the server
                time.sleep(2)

        # And we update the last_roster_update date
        options = Options.objects.all()
        if options.exists():
            options = options.get()
        else:
            options = Options()
        options.last_roster_update = timezone.now()
        options.save()

        if errors:
            self.stdout.write("ERRORS")
            for error in errors:
                self.stdout.write(f"{error['player']}, {error['error']}")
        if faceless:
            self.stdout.write("FACELESS")
            for player in faceless:
                self.stdout.write(player)

        end_time = timezone.now()
        self.stdout.write("Started")
        self.stdout.write(str(start_time))
        self.stdout.write("Ended")
        self.stdout.write(str(end_time))
        self.stdout.write("Elapsed")
        self.stdout.write(str(end_time - start_time))
