# -*- encoding: utf-8 -*-
import requests
import json
import os.path
from .teams import (ALL_TEAMS, PLAYOFF_TEAMS, EAST_TEAMS, WEST_TEAMS, )
from .models import (Player, Team, )
from datetime import (datetime, timedelta, )


def team_to_dict(team):
    return {
        'nba_id': team.nba_id,
        'city': team.city,
        'name': team.name,
        'abbreviation': team.abbreviation,
        'code': team.code,
        'picture': team.picture,
    }


def player_to_dict(player):
    return {
        'nba_id': player.nba_id,
        'name': player.name,
        'team': team_to_dict(player.team),
        'picture': player.picture,
    }


def get_teams_and_players_database(limit_teams):
    players = []
    teams = []
    LIMIT_TEAMS = {
        'all': Team.objects.all(),
        'playoffs': Team.objects.filter(code__in=PLAYOFF_TEAMS),
        'east': Team.objects.filter(division__conference__name='East'),
        'west': Team.objects.filter(division__conference__name='West'),
    }
    LIMIT_PLAYERS = {
        'all': Player.objects.all(),
        'playoffs': Player.objects.filter(team__code__in=PLAYOFF_TEAMS),
        'east': Player.objects.filter(
            team__division__conference__name='East'
        ),
        'west': Player.objects.filter(
            team__division__conference__name='West'
        ),
    }

    for team in LIMIT_TEAMS[limit_teams]:
        t = team_to_dict(team)
        teams.append(t)

    for player in LIMIT_PLAYERS[limit_teams]:
        p = player_to_dict(player)
        players.append(p)

    return (teams, players)


def get_players_api():
    dt = datetime.today().date()
    tries_left = 3
    while tries_left > 0:
        filename = dt.strftime("%Y%m%d") + ".json"
        if os.path.isfile(filename):
            try:
                with open(filename, 'r') as f:
                    data = f.read()
                    j = json.loads(data)
                return j['resultSets'][0]['rowSet']
            except:
                os.remove(filename)
        dt = dt - timedelta(days=1)
        tries_left -= 1

    PLAYERS_URL = "http://stats.nba.com/stats/commonallplayers"\
        "?IsOnlyCurrentSeason=1&LeagueID=00&Season=2015-16"
    r = requests.get(PLAYERS_URL)

    try:
        j = r.json()
        dt = datetime.today().date()
        filename = dt.strftime("%Y%m%d") + ".json"
        with open(filename, 'w') as f:
            f.write(r.text)
    except ValueError:
        return
        # raise Http404("There's been a problem fetching info from NBA.com")

    return j['resultSets'][0]['rowSet']


def get_teams_and_players_api(limit_teams):
    LIMIT_TEAMS = {
        'all': ALL_TEAMS,
        'playoffs': PLAYOFF_TEAMS,
        'east': EAST_TEAMS,
        'west': WEST_TEAMS,
    }

    PLAYER_PICTURE_URL = "http://i.cdn.turner.com/nba/nba/.element/img/"\
        "2.0/sect/statscube/players/large/%s.png"
    TEAM_PICTURE_URL = "http://stats.nba.com/media/img/teams/logos/%s_logo.svg"

    nba_players = get_players_api()
    players = []
    teams = []

    allowed_teams = LIMIT_TEAMS[limit_teams]

    faceless = [204098, 1626162, 1627362, 1626210]
    for p in nba_players:
        # Roster status

        if p[3] != 0 and p[0] not in faceless:
            if p[11] not in allowed_teams:
                continue
            team = {
                'nba_id': p[7],
                'city': p[8],
                'name': p[9],
                'abbreviation': p[10],
                'code': p[11],
                'picture': TEAM_PICTURE_URL % p[10],
            }
            if team not in teams:
                teams.append(team)

            player = {
                'nba_id': p[0],
                'name': p[2],
                'team': team,
                'picture': PLAYER_PICTURE_URL % p[6],
            }
            players.append(player)

    teams = sorted(teams)
    # player = random.choice(players)
    return (teams, players)
