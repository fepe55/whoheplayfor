# -*- encoding: utf-8 -*-
import requests
import time

from whpf.views import get_players


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
                print 'has a face!'
            elif r.status_code == 404:
                f.write(str(p[0]))
                f.write('\n')
                print 'has no face'
            else:
                print 'error', p

        time.sleep(2)

    f.close()

# meant to be run from the project root as `python -m utils.find_faceless`
if __name__ == '__main__':
    get_faceless()
