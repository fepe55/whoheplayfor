# -*- encoding: utf-8 -*-

import random
import json
import requests
from flask import (Flask, render_template, )
app = Flask(__name__)


@app.route('/')
def hello_world():
    PLAYERS_URL = "http://stats.nba.com/stats/commonallplayers?IsOnlyCurrentSeason=1&LeagueID=00&Season=2015-16"
    PLAYER_PICTURE_URL = "http://i.cdn.turner.com/nba/nba/.element/img/2.0/sect/statscube/players/large/%s.png"
    TEAM_PICTURE_URL = "http://stats.nba.com/media/img/teams/logos/%s_logo.svg"
    r = requests.get(PLAYERS_URL)
    j = json.loads(r.text)
    nba_players = j['resultSets'][0]['rowSet']
    players = []
    teams = []
    for p in nba_players:
        # Roster status
        if p[3] != 0:
            team = {
                'city': p[8],
                'name': p[9],
                'abbreviation': p[10],
                'code': p[11],
                'picture': TEAM_PICTURE_URL % p[10],
            }
            if team not in teams:
                teams.append(team)

            player = {
                'name': p[2],
                'team': team,
                'picture': PLAYER_PICTURE_URL % p[6],
            }
            players.append(player)

    teams = sorted(teams)
    player = random.choice(players)
    return render_template('whpf.html', player=player, teams=teams)

if __name__ == '__main__':
    app.run(debug=True, port=8000)
