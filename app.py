# -*- encoding: utf-8 -*-

import requests
import json
import os.path
from datetime import datetime

from flask import (Flask, render_template, abort, request, )
app = Flask(__name__)


def get_players():
    filename = datetime.today().date().strftime("%Y%m%d") + ".json"
    if os.path.isfile(filename):
        with open(filename, 'r') as f:
            data = f.read()
            j = json.loads(data)
    else:
        PLAYERS_URL = "http://stats.nba.com/stats/commonallplayers?IsOnlyCurrentSeason=1&LeagueID=00&Season=2015-16"
        r = requests.get(PLAYERS_URL)
        with open(filename, 'w') as f:
            f.write(r.text)
        try:
            j = r.json()
        except ValueError:
            abort(500, "There's been a problem fetching info from NBA.com")

    return j['resultSets'][0]['rowSet']


@app.route('/results/<code>')
def results(code):
    # code: level(1) + rounds(3) + n times (player_id(8), guess_id(2))
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
    return render_template('results.html', guesses=final_guesses,
                           game_info=game_info)


@app.route('/tv')
def tv():
    videos = ['6psHr028Hyg', 'nvZt5d8RFr0', 'KbatKgTdRkM', 'cAIPKDBC4Mg', ]
    return render_template('tv.html', videos=videos)


@app.route('/', methods=['GET', 'POST', ])
def home():
    TIMES = [0, 30, 60, 90]
    ROUNDS = [10, 20, 30]

    if request.method != 'POST':
        return render_template('home.html')

    time = int(request.form['time'])
    rounds = int(request.form['rounds'])
    if time not in TIMES or rounds not in ROUNDS:
        abort(400)

    game_info = {
        'show_player_name': 'show_player_name' in request.form,
        'shuffle_teams': 'shuffle_teams' in request.form,
        'time': time,
        'rounds': rounds,
    }

    PLAYER_PICTURE_URL = "http://i.cdn.turner.com/nba/nba/.element/img/2.0/sect/statscube/players/large/%s.png"
    TEAM_PICTURE_URL = "http://stats.nba.com/media/img/teams/logos/%s_logo.svg"

    nba_players = get_players()
    players = []
    teams = []
    faceless = [204098, 1626162, 1627362, 1626210]
    for p in nba_players:
        # Roster status

        if p[3] != 0 and p[0] not in faceless:
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
    return render_template('whpf.html', players=players, teams=teams,
                           game_info=game_info)




if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8000)
