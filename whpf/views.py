# -*- encoding: utf-8 -*-
import json

from django.http import (HttpResponse, Http404, )
from django.shortcuts import (render, get_object_or_404, )
from django.core.urlresolvers import reverse

from .models import (Result, Player, Team, )
from .forms import (GameForm,
                    TIME_CHOICES, ROUNDS_CHOICES, LIMIT_TEAMS_CHOICES, )
from .helpers import (parse_code, get_score,
                      get_teams_and_players_database,
                      get_teams_and_players_api, )


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
        'time': time,
        'rounds': rounds,
        'limit_teams': limit_teams,
        'shuffle_teams': shuffle_teams,
        'show_player_name': show_player_name,
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
            "where <code>wrong_guesses</code> include not only the ones you "
            "didn't guess right, but also the rounds you did not play.<br />"
            "And <code>difficulty</code> starts being 1, and adds up like so:"
            "<ul>"
            "<li>2 if the players name are not shown.</li>"
            "<li>1 if the teams are shuffled.</li>"
            "<li>1 if you are playing with every team.</li>"
            "<li>3 if you set the time limit to 30 seconds.</li>"
            "<li>2 if you set the time limit to 60 seconds.</li>"
            "<li>1 if you set the time limit to 90 seconds.</li>"
            "</ul>"
            "While <code>correct_guesses</code> and "
            "<code>wrong_guesses</code> are... well, you know.<br />"
            "I'll eventually come up with a better way to calculate scores "
            "but for now, this'll have to do."
            "<strong>Important</strong>: If you play without a time limit, "
            "you'll get a score of 0."
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

    score = get_score(code)
    parsed_code = parse_code(code)
    results = Result.objects.filter(code=code)
    if results.count() == 1:
        result = results[0]
    else:
        result = None

    rounds_played = parsed_code['rounds_played']
    code = parsed_code['guesses']
    guesses = []
    for i in xrange(rounds_played):
        guess_str = code[10*i:10*i+10]
        player_id = int(guess_str[:8])
        team_id = int(guess_str[8:])
        p = get_object_or_404(Player, nba_id=player_id)
        t = get_object_or_404(Team, nba_id__endswith=team_id)
        guess = {
            'round': i+1,
            'player': p,
            'team': t,
        }
        guesses.append(guess)

    return render(request, 'results.html', {
        'guesses': guesses, 'score': score, 'result': result,
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


# types: 'right', 'wrong'
def guess(player_id, type_of_guess):
    player = get_object_or_404(Player, nba_id=player_id)
    if type_of_guess == 'right':
        player.times_guessed_right += 1
    if type_of_guess == 'wrong':
        player.times_guessed_wrong += 1
    player.save()
    return


def right_guess(request, pid):
    if request.is_ajax():
        guess(pid, 'right')
        to_json = {'success': True, }
        return HttpResponse(json.dumps(to_json),
                            content_type='application/json')
    else:
        raise Http404


def wrong_guess(request, pid):
    if request.is_ajax():
        guess(pid, 'wrong')
        to_json = {'success': True, }
        return HttpResponse(json.dumps(to_json),
                            content_type='application/json')
    else:
        raise Http404
