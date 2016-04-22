# -*- encoding: utf-8 -*-
import requests
import json
import os.path
from datetime import (datetime, timedelta, )

from django.http import Http404
from django.shortcuts import render

from .teams import (ALL_TEAMS, PLAYOFF_TEAMS, EAST_TEAMS, WEST_TEAMS, )
from .forms import (GameForm,
                    TIME_CHOICES, ROUNDS_CHOICES, LIMIT_TEAMS_CHOICES, )


def get_players():
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

    PLAYERS_URL = "http://stats.nba.com/stats/commonallplayers?IsOnlyCurrentSeason=1&LeagueID=00&Season=2015-16"
    r = requests.get(PLAYERS_URL)

    try:
        j = r.json()
        dt = datetime.today().date()
        filename = dt.strftime("%Y%m%d") + ".json"
        with open(filename, 'w') as f:
            f.write(r.text)
    except ValueError:
        raise Http404("There's been a problem fetching info from NBA.com")

    return j['resultSets'][0]['rowSet']


def home(request):
    TIME_DEFAULT = TIME_CHOICES[2][0]  # 60
    ROUNDS_DEFAULT = ROUNDS_CHOICES[1][0]  # 20
    LIMIT_TEAMS = {
        'all': ALL_TEAMS,
        'playoffs': PLAYOFF_TEAMS,
        'east': EAST_TEAMS,
        'west': WEST_TEAMS,
    }
    LT_DEFAULT = LIMIT_TEAMS_CHOICES[0][0]  # 'all'
    SPN_DEFAULT = True
    SF_DEFAULT = False

    time = request.session.get('time', TIME_DEFAULT)
    rounds = request.session.get('rounds', ROUNDS_DEFAULT)
    limit_teams = request.session.get('limit_teams', LT_DEFAULT)
    shuffle_teams = request.session.get('shuffle_teams', SF_DEFAULT)
    show_player_name = request.session.get('show_player_name', SPN_DEFAULT)

    form = GameForm(initial={
        'time': time,
        'rounds': rounds,
        'limit_teams': limit_teams,
        'shuffle_teams': shuffle_teams,
        'show_player_name': show_player_name,
    })

    if not request.POST:
        return render(request, "home.html", {'form': form, })

    form = GameForm(request.POST)

    if not form.is_valid():
        return render(request, "home.html", {'form': form, })

    time = int(form.cleaned_data['time'])
    rounds = int(form.cleaned_data['rounds'])
    limit_teams = form.cleaned_data['limit_teams']
    shuffle_teams = form.cleaned_data['shuffle_teams']
    show_player_name = form.cleaned_data['show_player_name']

    if (
        time not in [x[0] for x in TIME_CHOICES] or
        rounds not in [x[0] for x in ROUNDS_CHOICES] or
        limit_teams not in [x[0] for x in LIMIT_TEAMS_CHOICES]
    ):
        request.session.clear()
        raise Http404("Hola")

    request.session['time'] = time
    request.session['rounds'] = rounds
    request.session['limit_teams'] = limit_teams
    request.session['shuffle_teams'] = shuffle_teams
    request.session['show_player_name'] = show_player_name

    game_info = {
        'show_player_name': show_player_name,
        'shuffle_teams': shuffle_teams,
        'time': time,
        'rounds': rounds,
    }

    PLAYER_PICTURE_URL = "http://i.cdn.turner.com/nba/nba/.element/img/2.0/sect/statscube/players/large/%s.png"
    TEAM_PICTURE_URL = "http://stats.nba.com/media/img/teams/logos/%s_logo.svg"

    nba_players = get_players()
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
                'id': p[7],
                'city': p[8],
                'name': p[9],
                'abbreviation': p[10],
                'code': p[11],
                'picture': TEAM_PICTURE_URL % p[10],
            }
            if team not in teams:
                teams.append(team)

            player = {
                'id': p[0],
                'name': p[2],
                'team': team,
                'picture': PLAYER_PICTURE_URL % p[6],
            }
            players.append(player)

    teams = sorted(teams)
    # player = random.choice(players)
    return render(request, 'whpf.html', {
        'players': players, 'teams': teams, 'game_info': game_info,
    })


def tv(request):
    videos = ['6psHr028Hyg', 'nvZt5d8RFr0', 'KbatKgTdRkM', 'cAIPKDBC4Mg', ]
    return render(request, "tv.html", {'videos': videos})


def results(request, code):
    # code: show_player_name(1) + shuffle_teams(1) + time_limit(3) +
    # rounds(3) + n times (player_id(8), guess_id(2))

    show_player_name = int(code[:1])
    code = code[1:]

    shuffle_teams = int(code[:1])
    code = code[1:]

    time_limit = int(code[:3])
    code = code[3:]

    game_info = {
        'show_player_name': show_player_name,
        'shuffle_teams': shuffle_teams,
        'time_limit': time_limit,
    }

    rounds = int(code[:3])
    code = code[3:]
    guesses = []
    for i in xrange(rounds):
        guess_str = code[10*i:10*i+10]
        guess = {
            'round': i+1,
            'player_id': int(guess_str[:8]),
            'team_id': int(guess_str[8:]),
        }
        guesses.append(guess)

    PLAYER_PICTURE_URL = "http://i.cdn.turner.com/nba/nba/.element/img/2.0/sect/statscube/players/large/%s.png"
    TEAM_PICTURE_URL = "http://stats.nba.com/media/img/teams/logos/%s_logo.svg"

    nba_players = get_players()
    proper_guesses = {}
    for i in xrange(rounds):
        proper_guesses[i+1] = {}

    for p in nba_players:
        # Roster status
        for g in guesses:
            if p[0] == g['player_id']:
                team = {
                    'id': p[7],
                    'city': p[8],
                    'name': p[9],
                    'abbreviation': p[10],
                    'code': p[11],
                    'picture': TEAM_PICTURE_URL % p[10],
                }
                player = {
                    'id': p[0],
                    'name': p[2],
                    'team': team,
                    'picture': PLAYER_PICTURE_URL % p[6],
                }
                proper_guesses[g['round']]['player'] = player

            if int(str(p[7])[-2:]) == g['team_id']:
                team = {
                    'id': p[7],
                    'city': p[8],
                    'name': p[9],
                    'abbreviation': p[10],
                    'code': p[11],
                    'picture': TEAM_PICTURE_URL % p[10],
                }
                proper_guesses[g['round']]['team'] = team

        final_guesses = []
        for i in xrange(rounds):
            final_guesses.append(proper_guesses[i+1])

    return render(request, 'results.html', {
        'guesses': final_guesses, 'game_info': game_info
    })
