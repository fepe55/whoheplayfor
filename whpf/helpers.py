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
        '0': Team.objects.all(),
        '1': Team.objects.filter(division__conference__name='East'),
        '2': Team.objects.filter(division__conference__name='West'),
        '3': Team.objects.filter(code__in=PLAYOFF_TEAMS),
    }
    LIMIT_PLAYERS = {
        '0': Player.objects.all(),
        '1': Player.objects.filter(
            team__division__conference__name='East'
        ),
        '2': Player.objects.filter(
            team__division__conference__name='West'
        ),
        '3': Player.objects.filter(team__code__in=PLAYOFF_TEAMS),
    }

    for team in LIMIT_TEAMS[limit_teams]:
        t = team_to_dict(team)
        teams.append(t)

    for player in LIMIT_PLAYERS[limit_teams]:
        p = player_to_dict(player)
        players.append(p)

    return (teams, players)


def get_players_api():
    # dt = datetime.today().date()
    # tries_left = 3
    # while tries_left > 0:
    #     filename = dt.strftime("%Y%m%d") + ".json"
    #     if os.path.isfile(filename):
    #         try:
    #             with open(filename, 'r') as f:
    #                 data = f.read()
    #                 j = json.loads(data)
    #             return j['resultSets'][0]['rowSet']
    #         except:
    #             os.remove(filename)
    #     dt = dt - timedelta(days=1)
    #     tries_left -= 1

    PLAYERS_URL = "http://stats.nba.com/stats/commonallplayers"\
        "?IsOnlyCurrentSeason=1&LeagueID=00&Season=2015-16"
    r = requests.get(PLAYERS_URL)

    try:
        j = r.json()
        # dt = datetime.today().date()
        # filename = dt.strftime("%Y%m%d") + ".json"
        # with open(filename, 'w') as f:
        #     f.write(r.text)
    except ValueError:
        print "There's been a problem fetching info from NBA.com"
        return
        # raise Http404("There's been a problem fetching info from NBA.com")

    return j['resultSets'][0]['rowSet']


def get_teams_and_players_api(limit_teams):
    LIMIT_TEAMS = {
        '0': ALL_TEAMS,
        '1': EAST_TEAMS,
        '2': WEST_TEAMS,
        '3': PLAYOFF_TEAMS,
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
    parsed_code = parse_code(code)
    rounds_played = parsed_code['rounds_played']
    code = parsed_code['guesses']
    guesses = []
    for i in xrange(rounds_played):
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
    parsed_code = parse_code(code)
    show_player_name = parsed_code['show_player_name']
    shuffle_teams = parsed_code['shuffle_teams']
    time_limit = parsed_code['time_limit']
    limit_teams = parsed_code['limit_teams']
    if not show_player_name:
        difficulty += 2
    if shuffle_teams:
        difficulty += 1
    if limit_teams == 0:  # All teams
        difficulty += 1
    if time_limit:
        difficulty += (4 - time_limit/30)
    else:
        difficulty = 0
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

    parsed_code = parse_code(code)
    wrong_guesses += parsed_code['total_rounds'] - parsed_code['rounds_played']
    score = (3*correct_guesses - wrong_guesses) * difficulty
    # score = score*100 + parsed_code['time_left']
    return score


def parse_code(code):
    # code: show_player_name(1) + shuffle_teams(1) + limit_teams(2) +
    # time_left(3) + time_limit(3) +
    # rounds_played(3) + total_rounds(3) +
    # n times (player_id(8), guess_id(2))
    show_player_name = code[:1] == '1'
    shuffle_teams = code[1:2] == '1'
    limit_teams = int(code[2:4])
    time_left = int(code[4:7])
    time_limit = int(code[7:10])
    rounds_played = int(code[10:13])
    total_rounds = int(code[13:16])
    guesses = code[16:]

    return {
        'show_player_name': show_player_name,
        'shuffle_teams': shuffle_teams,
        'time_left': time_left,
        'time_limit': time_limit,
        'rounds_played': rounds_played,
        'total_rounds': total_rounds,
        'guesses': guesses,
        'limit_teams': limit_teams,
    }
