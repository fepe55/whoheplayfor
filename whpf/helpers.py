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


# SCORE

def get_guesses(code):
    code = code[1:]  # show_player_name
    code = code[1:]  # shuffle_teams
    code = code[3:]  # time_limit
    rounds = int(code[:3])
    code = code[3:]  # rounds
    guesses = []
    for i in xrange(rounds):
        guess_str = code[10*i:10*i+10]
        player_id = int(guess_str[:8])
        player = Player.objects.get(nba_id=player_id)
        team_id = int(guess_str[8:])
        team = Team.objects.get(nba_id__endswith=team_id)
        guess = {
            'round': i+1,
            'player': player,
            'team': team,
        }
        guesses.append(guess)
    return guesses


def get_difficulty(code):
    difficulty = 1
    show_player_name = code[:1] == '1'
    shuffle_teams = code[1:2] == '1'
    if not show_player_name:
        difficulty += 2
    if shuffle_teams:
        difficulty += 1
    return difficulty


def get_score(code):
    correct_guesses = 0
    wrong_guesses = 0
    difficulty = get_difficulty(code)
    guesses = get_guesses(code)
    for guess in guesses:
        if guess['player'].team.id == guess['team'].id:
            correct_guesses += 1
        else:
            wrong_guesses += 1

    score = (3*correct_guesses - wrong_guesses) * difficulty
    return score
