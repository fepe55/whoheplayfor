# -*- encoding: utf-8 -*-
import json

from django.http import (HttpResponse, Http404, )
from django.shortcuts import render
from django.core.urlresolvers import reverse

from .models import Result
from .forms import (GameForm,
                    TIME_CHOICES, ROUNDS_CHOICES, LIMIT_TEAMS_CHOICES, )
from .helpers import (get_teams_and_players_database,
                      get_teams_and_players_api,
                      get_players_api, get_score, )


def get_teams_and_players(limit_teams):
    database = True
    if database:
        return get_teams_and_players_database(limit_teams)
    else:
        return get_teams_and_players_api(limit_teams)


def home(request):
    TIME_DEFAULT = TIME_CHOICES[2][0]  # 60
    ROUNDS_DEFAULT = ROUNDS_CHOICES[1][0]  # 20
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
        raise Http404()

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

    (teams, players) = get_teams_and_players(limit_teams)

    return render(request, 'whpf.html', {
        'players': players, 'teams': teams, 'game_info': game_info,
    })


def tv(request):
    videos = ['6psHr028Hyg', 'nvZt5d8RFr0', 'KbatKgTdRkM', 'cAIPKDBC4Mg', ]
    return render(request, "tv.html", {'videos': videos})


def faq(request):
    tv_url = reverse("whpf:tv")
    questions = [
        {
            'id': 'whoareyou',
            'question': "Who are you?",
            'answer': "I'm Fepe. Hi."
        },
        {
            'id': 'idea',
            'question': "Where did you get the idea to do this?",
            'answer': "<strong>Who He Play For?</strong> is a recurrent game "
            "on <a href='"+tv_url+"' %}'>Inside the NBA</a>, where Ernie asks "
            "Chuck to guess where certain players play. And I've always "
            "found the idea fun to play. So I made it into a web game, so I "
            "(and you) can play it."

        },
        {
            'id': "scores",
            'question': "How are scores calculated?",
            'answer': "It's a work in progress, so it can change anytime. "
            "For now, it's simply "
            "<code>(3*correct_guesses - wrong_guesses) * difficulty</code> "
            "where <code>difficulty</code> starts being 1, and adds 2 if "
            "the players name are not shown, and 1 if the teams are shuffled. "
            "While <code>correct_guesses</code> and "
            "<code>wrong_guesses</code> are... well, you know."
        },
        {
            'id': 'roster',
            'question': "How updated are the rosters?",
            'answer': "They are updated as of April 25th, 2016."
        },
        {
            'id': 'contact',
            'question': "I have a question/suggestion/complaint, how can I "
            "contact you?",
            'answer': "If what you want is not covered in this FAQ, you can "
            "find me at <a href='http://reddit.com/u/fepe55'>"
            "<i class='fa fa-reddit-alien'></i> /u/fepe55</a> and "
            "at <a href='http://twitter.com/fepe55/'>"
            "<i class='fa fa-twitter'></i> @fepe55</a>."
        },
    ]
    return render(request, "faq.html", {'questions': questions, })


def save(request, code):
    if request.is_ajax():
        r = Result.objects.create(user=request.user, code=code, )
        r.calculate_score()
        to_json = {'success': True, }
        return HttpResponse(json.dumps(to_json),
                            content_type='application/json')
    else:
        raise Http404


def results(request, code):
    # code: show_player_name(1) + shuffle_teams(1) + time_limit(3) +
    # rounds(3) + n times (player_id(8), guess_id(2))

    score = get_score(code)

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

    PLAYER_PICTURE_URL = "http://i.cdn.turner.com/nba/nba/.element/img/2.0/"\
        "sect/statscube/players/large/%s.png"
    TEAM_PICTURE_URL = "http://stats.nba.com/media/img/teams/logos/%s_logo.svg"

    nba_players = get_players_api()
    if not nba_players:
        raise Http404
    proper_guesses = {}
    for i in xrange(rounds):
        proper_guesses[i+1] = {}

    for p in nba_players:
        # Roster status
        for g in guesses:
            if p[0] == g['player_id']:
                team = {
                    'nba_id': p[7],
                    'city': p[8],
                    'name': p[9],
                    'abbreviation': p[10],
                    'code': p[11],
                    'picture': TEAM_PICTURE_URL % p[10],
                }
                player = {
                    'nba_id': p[0],
                    'name': p[2],
                    'team': team,
                    'picture': PLAYER_PICTURE_URL % p[6],
                }
                proper_guesses[g['round']]['player'] = player

            if int(str(p[7])[-2:]) == g['team_id']:
                team = {
                    'nba_id': p[7],
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
        'guesses': final_guesses, 'game_info': game_info, 'score': score,
    })


def scoreboard(request):
    results = Result.objects.all()[:10]
    return render(request, 'scoreboard.html', {'scores': results, })


def score(request, code):
    if request.is_ajax():
        to_json = {'score': get_score(code), }
        return HttpResponse(json.dumps(to_json),
                            content_type='application/json')
    else:
        raise Http404
