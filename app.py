# -*- encoding: utf-8 -*-

import requests
from flask import (Flask, render_template, abort, )
app = Flask(__name__)


@app.route('/results/<code>')
def results(code):
    # code: level(1) + rounds(3) + n times (player_id(8), guess_id(2))

    level = int(code[:1])
    code = code[1:]
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

    PLAYERS_URL = "http://stats.nba.com/stats/commonallplayers?IsOnlyCurrentSeason=1&LeagueID=00&Season=2015-16"
    PLAYER_PICTURE_URL = "http://i.cdn.turner.com/nba/nba/.element/img/2.0/sect/statscube/players/large/%s.png"
    TEAM_PICTURE_URL = "http://stats.nba.com/media/img/teams/logos/%s_logo.svg"

    r = requests.get(PLAYERS_URL)
    try:
        j = r.json()
    except ValueError:
        abort(500, "There's been a problem fetching info from NBA.com")

    nba_players = j['resultSets'][0]['rowSet']
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
                           level=level)


@app.route('/lvl/<level>')
def game(level):
    level = int(level)
    if level < 0 or level > 4:
        abort(404)

    PLAYERS_URL = "http://stats.nba.com/stats/commonallplayers?IsOnlyCurrentSeason=1&LeagueID=00&Season=2015-16"
    PLAYER_PICTURE_URL = "http://i.cdn.turner.com/nba/nba/.element/img/2.0/sect/statscube/players/large/%s.png"
    TEAM_PICTURE_URL = "http://stats.nba.com/media/img/teams/logos/%s_logo.svg"

    r = requests.get(PLAYERS_URL)
    try:
        j = r.json()
    except ValueError:
        print dir(r)
        abort(500, "There's been a problem fetching info from NBA.com")

    nba_players = j['resultSets'][0]['rowSet']
    players = []
    teams = []
    for p in nba_players:
        # Roster status
        if p[3] != 0:
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
                           level=level)


@app.route('/')
def home():
    return render_template('home.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8000)
