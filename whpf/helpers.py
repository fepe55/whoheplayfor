# -*- encoding: utf-8 -*-
import requests
import json
from .teams import (
    ALL_TEAMS, EAST_TEAMS, WEST_TEAMS,
    PLAYOFF_TEAMS_2016, FINALS_TEAMS_2016,
    PLAYOFF_TEAMS_2017,
)
from .models import Team, Player, Division, Conference
from whpf.teams import (
    ATLANTIC_TEAMS, CENTRAL_TEAMS, SOUTHEAST_TEAMS,
    NORTHWEST_TEAMS, PACIFIC_TEAMS, SOUTHWEST_TEAMS,
    TEAMS_ID,
)


def start_data():
    """
    Populates the database with everything for the first time.
    Conferences, divisiones, teams and players
    """

    # First, we create the conferences
    east, _ = Conference.objects.get_or_create(name='East')
    west, _ = Conference.objects.get_or_create(name='West')

    # Second, we create the divisions
    atlantic, _ = Division.objects.get_or_create(
        name='Atlantic', conference=east
    )
    central, _ = Division.objects.get_or_create(
        name='Central', conference=east
    )
    southeast, _ = Division.objects.get_or_create(
        name='Southeast', conference=east
    )

    northwest, _ = Division.objects.get_or_create(
        name='Northwest', conference=west
    )
    pacific, _ = Division.objects.get_or_create(
        name='Pacific', conference=west
    )
    southwest, _ = Division.objects.get_or_create(
        name='Southwest', conference=west
    )

    # Third, we create the teams
    nba_players = get_players_api()

    # al_atlantic = False
    # al_central = False
    # al_southeast = False
    # al_northwest = False
    # al_pacific = False
    # al_southwest = False
    # mocked_nba_players = []

    # for p in nba_players:
    #     team_code = p[5]
    #     if team_code in ATLANTIC_TEAMS:
    #         if not al_atlantic:
    #             mocked_nba_players.append(p)
    #             al_atlantic = True
    #     if team_code in CENTRAL_TEAMS:
    #         if not al_central:
    #             mocked_nba_players.append(p)
    #             al_central = True
    #     if team_code in SOUTHEAST_TEAMS:
    #         if not al_southeast:
    #             mocked_nba_players.append(p)
    #             al_southeast = True
    #     if team_code in NORTHWEST_TEAMS:
    #         if not al_northwest:
    #             mocked_nba_players.append(p)
    #             al_northwest = True
    #     if team_code in PACIFIC_TEAMS:
    #         if not al_pacific:
    #             mocked_nba_players.append(p)
    #             al_pacific = True
    #     if team_code in SOUTHWEST_TEAMS:
    #         if not al_southwest:
    #             mocked_nba_players.append(p)
    #             al_southwest = True

    #     if all([
    #         al_atlantic, al_central, al_southeast, al_northwest, al_pacific,
    #         al_southwest
    #     ]):
    #         print(mocked_nba_players)
    #         a = 1/0

    # b = 1 / 0
    for p in nba_players:
        # team_city = p['teamData']['city']
        # team_name = p['teamData']['nickname']
        # team_abbreviation = p['teamData']['tricode']
        # team_code = p['teamData']['urlName']
        if p[4] == 0:
            continue
        team_city = p[7]
        team_name = p[8]
        team_abbreviation = p[9]
        team_code = p[5]
        team_nba_id = TEAMS_ID[team_code]

        if not Team.objects.filter(nba_id=team_nba_id).exists():
            if team_code in ATLANTIC_TEAMS:
                division = atlantic
            if team_code in CENTRAL_TEAMS:
                division = central
            if team_code in SOUTHEAST_TEAMS:
                division = southeast
            if team_code in NORTHWEST_TEAMS:
                division = northwest
            if team_code in PACIFIC_TEAMS:
                division = pacific
            if team_code in SOUTHWEST_TEAMS:
                division = southwest

            Team.objects.create(
                nba_id=team_nba_id,
                city=team_city,
                name=team_name,
                abbreviation=team_abbreviation,
                code=team_code,
                division=division,
            )

    # And fourth, we create the players
    # We loop twice on the nba_players for an easier code to read
    # faceless = [204098, 1626162, 1626210]
    faceless = []
    for p in nba_players:
        if p[4] == 0:
            continue

        team_code = p[5]
        team_nba_id = TEAMS_ID[team_code]

        nba_id = int(p[0])
        name = '{} {}'.format(p[2], p[1])
        code = name.replace(' ', '_').lower()

        team = Team.objects.get(nba_id=team_nba_id)
        fl = nba_id in faceless
        player_qs = Player.all_players.filter(nba_id=nba_id)
        if not player_qs.exists():
            Player.objects.create(
                nba_id=nba_id,
                name=name,
                team=team,
                code=code,
                faceless=fl,
            )


def team_to_dict(team):
    """Take a Team object and return a dictionary with the following
    fields:
    nba_id, city, name, abbreviation, code, picture
    """
    return {
        'nba_id': team.nba_id,
        'city': team.city,
        'name': team.name,
        'abbreviation': team.abbreviation,
        'code': team.code,
        'picture': team.picture,
    }


def player_to_dict(player):
    """Take a Player object and return a dictionary with the following
    fields:
    nba_id, name, team, picture.
    """
    return {
        'nba_id': player.nba_id,
        'name': player.name,
        'team': team_to_dict(player.team),
        'picture': player.picture,
    }


def get_teams_and_players_database(game_info):
    """Get teams and players from the database."""
    players = []
    teams = []
    limit_teams = game_info['limit_teams']
    hard_mode = game_info['hard_mode']

    LIMIT_TEAMS = {
        '0': Team.objects.all(),
        '1': Team.objects.filter(division__conference__name='East'),
        '2': Team.objects.filter(division__conference__name='West'),
        '3': Team.objects.filter(code__in=PLAYOFF_TEAMS_2016),
        '4': Team.objects.filter(code__in=FINALS_TEAMS_2016),
        '5': Team.objects.filter(code__in=PLAYOFF_TEAMS_2017),
    }
    LIMIT_PLAYERS = {
        '0': Player.objects.all(),
        '1': Player.objects.filter(
            team__division__conference__name='East'
        ),
        '2': Player.objects.filter(
            team__division__conference__name='West'
        ),
        '3': Player.objects.filter(team__code__in=PLAYOFF_TEAMS_2016),
        '4': Player.objects.filter(team__code__in=FINALS_TEAMS_2016),
        '5': Player.objects.filter(team__code__in=PLAYOFF_TEAMS_2017),
    }

    for team in LIMIT_TEAMS[limit_teams]:
        t = team_to_dict(team)
        teams.append(t)

    players_qs = LIMIT_PLAYERS[limit_teams]

    # 50 hardest players
    if hard_mode:
        players_qs = players_qs.order_by('times_guessed_pct')[:50]

    for player in players_qs:
        p = player_to_dict(player)
        players.append(p)

    return (teams, players)


def get_players_api():
    """Get players from the NBA.com API."""
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

    # v1.0
    # PLAYERS_URL = "http://stats.nba.com/stats/commonallplayers/"
    # PARAMS = {
    #     'IsOnlyCurrentSeason': 1,
    #     'LeagueID': "00",
    #     'Season': "2017-18"
    # }

    # v2.0
    # PLAYERS_URL = "http://www.nba.com/players/active_players.json"
    # PARAMS = {}
    # HEADERS = {
    #     'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) '
    #     'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 '
    #     'Safari/537.36',
    #     'referer': 'http://stats.nba.com/scores/'
    # }

    # v3.0

    PLAYERS_URL = 'https://stats.nba.com/stats/playerindex'
    PARAMS = {
        'Historical': '0',
        'LeagueID': '00',
        'Season': '2021-22',
    }
    HEADERS = {
        'User-Agent': (
            'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:82.0) '
            'Gecko/20100101 Firefox/82.0'
        ),
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.nba.com/players',
        'Origin': 'https://www.nba.com',
        'Connection': 'keep-alive',
        'Accept-Encoding': 'compress',
    }

    # r = requests.get(PLAYERS_URL, params=PARAMS, headers=HEADERS)

    import os.path
    import os
    filename = 'players.json'
    if os.path.isfile(filename):
        with open(filename) as players_file:
            j = json.load(players_file)
        # We delete it so we don't use it again by mistake
        os.remove(filename)
    else:
        try:
            r = requests.get(PLAYERS_URL, params=PARAMS, headers=HEADERS)

        except requests.exceptions.RequestException as e:
            print(e)
            return []

        try:
            j = r.json()
            # dt = datetime.today().date()
            # filename = dt.strftime("%Y%m%d") + ".json"
            # with open(filename, 'w') as f:
            #     f.write(r.text)
        except ValueError:
            print("There's been a problem fetching info from NBA.com")
            return []
            # raise Http404("There's been a problem getting info from NBA.com")

    # return j
    return j['resultSets'][0]['rowSet']


# Deprecated
def get_teams_and_players_api(game_info):
    """(DEPRECATED) Get players and teams from the NBA.com API."""
    LIMIT_TEAMS = {
        '0': ALL_TEAMS,
        '1': EAST_TEAMS,
        '2': WEST_TEAMS,
        '3': PLAYOFF_TEAMS_2016,
        '4': FINALS_TEAMS_2016,
        '5': PLAYOFF_TEAMS_2017,
    }

    # PLAYER_PICTURE_URL = "http://i.cdn.turner.com/nba/nba/.element/img/"\
    #     "2.0/sect/statscube/players/large/%s.png"
    PLAYER_PICTURE_URL = "https://ak-static.cms.nba.com/wp-content/"\
        "uploads/headshots/nba/latest/260x190/%s.png"

    # TEAM_PICTURE_URL = "http://stats.nba.com/media/img/teams/logos/"\
    #     "%s_logo.svg"
    TEAM_PICTURE_URL = "https://i.cdn.turner.com/nba/nba/assets/logos/"\
        "teams/primary/web/%s.svg"

    nba_players = get_players_api()
    limit_teams = game_info['limit_teams']
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
    """Parse the code to get a list of guesses.
    Each guess is a dictionary with the following fields:
        - round: int
        - player: Player object
        - team: Team object
        - correct_team: Team object
    """
    parsed_code = parse_code(code)
    rounds_played = parsed_code['rounds_played']
    code = parsed_code['guesses']
    guesses = []
    for i in range(rounds_played):
        guess_str = code[12*i:12*i+12]
        player_id = int(guess_str[:8])
        if Player.all_players.filter(nba_id=player_id).exists():

            player = Player.all_players.get(nba_id=player_id)
            team_id = int(guess_str[8:10])
            team = Team.objects.get(nba_id__endswith=team_id)
            correct_team_id = int(guess_str[10:])
            correct_team = Team.objects.get(nba_id__endswith=correct_team_id)
            guess = {
                'round': i+1,
                'player': player,
                'team': team,
                'correct_team': correct_team,
            }
            guesses.append(guess)
    return guesses


def get_difficulty(code):
    """Parse the code to get game options and calculate the difficulty
    value.
    """
    parsed_code = parse_code(code)
    difficulty = 0
    hard_mode = parsed_code['hard_mode']
    show_player_name = parsed_code['show_player_name']
    shuffle_teams = parsed_code['shuffle_teams']
    time_limit = parsed_code['time_limit']
    limit_teams = parsed_code['limit_teams']
    total_rounds = parsed_code['total_rounds']
    # Defaults
    if time_limit == 60 and total_rounds == 20 and limit_teams == 0 \
            and not shuffle_teams and show_player_name:
        if hard_mode:
            difficulty = 1.5
        else:
            difficulty = 1
    return difficulty

    # # OLD Code
    # difficulty = 1
    # parsed_code = parse_code(code)
    # show_player_name = parsed_code['show_player_name']
    # shuffle_teams = parsed_code['shuffle_teams']
    # time_limit = parsed_code['time_limit']
    # limit_teams = parsed_code['limit_teams']
    # if not show_player_name:
    #     difficulty += 2
    # if shuffle_teams:
    #     difficulty += 1
    # if limit_teams == 0:  # All teams
    #     difficulty += 1
    # if time_limit:
    #     difficulty += (4 - time_limit/30)
    # else:
    #     difficulty = 0
    # return difficulty


def get_score(code):
    """Parse the code to obtain the score based on guesses."""
    correct_guesses = 0
    wrong_guesses = 0
    difficulty = get_difficulty(code)
    guesses = get_guesses(code)
    for guess in guesses:
        if guess['correct_team'].id == guess['team'].id:
            correct_guesses += 1
        else:
            wrong_guesses += 1

    parsed_code = parse_code(code)
    wrong_guesses += parsed_code['total_rounds'] - parsed_code['rounds_played']
    score = int(round(difficulty * 3 * correct_guesses - wrong_guesses))
    # score = score*100 + parsed_code['time_left']
    return score


def parse_code(code):
    """Parse code to obtain main options value."""
    if code[0] == 'v':
        # code: 'v' + version_number (3) + code
        version = code[1:4]
        if version == '001':
            # code: hard_mode(1) + show_player_name(1) + shuffle_teams(1) +
            # limit_teams(2) + time_left(3) + time_limit(3) +
            # rounds_played(3) + total_rounds(3) +
            # n times (player_id(8), guess_id(2), correct_team_id(2))
            code = code[4:]

            hard_mode = code[:1] == '1'
            show_player_name = code[1:2] == '1'
            shuffle_teams = code[2:3] == '1'
            limit_teams = int(code[3:5])
            time_left = int(code[5:8])
            time_limit = int(code[8:11])
            rounds_played = int(code[11:14])
            total_rounds = int(code[14:17])
            guesses = code[17:]

    # LEGACY
    else:
        # LEGACY code: show_player_name(1) + shuffle_teams(1) +
        # limit_teams(2) + time_left(3) + time_limit(3) +
        # rounds_played(3) + total_rounds(3) +
        # n times (player_id(8), guess_id(2), correct_team_id(2))
        hard_mode = False
        show_player_name = code[:1] == '1'
        shuffle_teams = code[1:2] == '1'
        limit_teams = int(code[2:4])
        time_left = int(code[4:7])
        time_limit = int(code[7:10])
        rounds_played = int(code[10:13])
        total_rounds = int(code[13:16])
        guesses = code[16:]

    return {
        'hard_mode': hard_mode,
        'show_player_name': show_player_name,
        'shuffle_teams': shuffle_teams,
        'time_left': time_left,
        'time_limit': time_limit,
        'rounds_played': rounds_played,
        'total_rounds': total_rounds,
        'guesses': guesses,
        'limit_teams': limit_teams,
    }
