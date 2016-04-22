# -*- encoding: utf-8 -*-
from datetime import datetime
import requests
import json
import os.path
import time


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
            print "Error"

    return j['resultSets'][0]['rowSet']


def get_faceless():
    PLAYER_PICTURE_URL = "http://i.cdn.turner.com/nba/nba/.element/img/2.0/sect/statscube/players/large/%s.png"
    players = get_players()
    f = open('faceless.txt', 'w')
    for p in players[300:]:
        if p[3] != 0:
            print p[0], p[2],
            picture = PLAYER_PICTURE_URL % p[6]
            r = requests.get(picture)
            if r.status_code == 200:
                print 'sí'
            elif r.status_code == 404:
                f.write(str(p[0]))
                f.write('\n')
                print 'no'
            else:
                print 'error', p

        time.sleep(2)

    f.close()

if __name__ == '__main__':
    get_faceless()
