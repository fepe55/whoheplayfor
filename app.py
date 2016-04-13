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
    r = requests.get(PLAYERS_URL)
    j = json.loads(r.text)
    nba_players = j['resultSets'][0]['rowSet']
    players = []
    teams = []
    for p in nba_players:
        # Roster status
        if p[3] != 0:
            player = {
                'name': p[2],
                'team': p[10],
                'picture': PLAYER_PICTURE_URL % p[6],
            }
            players.append(player)
            if p[10] not in teams:
                teams.append(p[10])

    teams = sorted(teams)
    player = random.choice(players)
    return render_template('whpf.html', player=player, teams=teams)

if __name__ == '__main__':
    app.run(debug=True, port=8000)
