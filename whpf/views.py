# -*- encoding: utf-8 -*-
import json
from datetime import timedelta

from django.http import (HttpResponse, Http404, )
from django.utils import (formats, timezone, )
from django.shortcuts import (render, get_object_or_404, )
from django.core.urlresolvers import reverse

from .models import (Result, Player, Options)
from .forms import (GameForm,
                    TIME_CHOICES, ROUNDS_CHOICES, LIMIT_TEAMS_CHOICES, )
from .helpers import (parse_code, get_score, get_guesses,
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

    # time = request.session.get('time', TIME_DEFAULT)
    # rounds = request.session.get('rounds', ROUNDS_DEFAULT)
    # limit_teams = request.session.get('limit_teams', LT_DEFAULT)
    # shuffle_teams = request.session.get('shuffle_teams', SF_DEFAULT)
    # show_player_name = request.session.get('show_player_name', SPN_DEFAULT)

    # form = GameForm(initial={
    #     'time': time,
    #     'rounds': rounds,
    #     'limit_teams': limit_teams,
    #     'shuffle_teams': shuffle_teams,
    #     'show_player_name': show_player_name,
    # })

    form = GameForm(initial={
        'time': TIME_DEFAULT,
        'rounds': ROUNDS_DEFAULT,
        'limit_teams': LT_DEFAULT,
        'shuffle_teams': SF_DEFAULT,
        'show_player_name': SPN_DEFAULT,
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
        # request.session.clear()
        raise Http404()

    # request.session['time'] = time
    # request.session['rounds'] = rounds
    # request.session['limit_teams'] = limit_teams
    # request.session['shuffle_teams'] = shuffle_teams
    # request.session['show_player_name'] = show_player_name

    game_info = {
        'time': time,
        'rounds': rounds,
        'limit_teams': limit_teams,
        'shuffle_teams': shuffle_teams,
        'show_player_name': show_player_name,
    }

    (teams, players) = get_teams_and_players(limit_teams)

    data = {
        'game_info': game_info,
        'players': players,
        'teams': teams,
    }

    if limit_teams == '0':
        data['west'] = teams[15:]
        data['east'] = teams[:15]

    return render(request, 'whpf.html', data)


def tv(request):
    videos = ['6psHr028Hyg', 'nvZt5d8RFr0', 'KbatKgTdRkM', 'cAIPKDBC4Mg', ]
    return render(request, "tv.html", {'videos': videos})


def faq(request):
    tv_url = reverse("whpf:tv")
    options = Options.objects.all()
    if options.exists():
        last_roster_update = formats.date_format(
            options.get().last_roster_update, "F jS, Y"
        )
    else:
        last_roster_update = ""
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
            "on <a href='"+tv_url+"'>Inside the NBA</a>, where Ernie asks "
            "Chuck to guess where certain players play. And I've always "
            "found the idea fun to play. So I made it into a web game, so I "
            "(and you) can play it."

        },
        {
            'id': 'players',
            'question': "Which players are there?",
            'answer': "Even though on <a href='"+tv_url+"'>Inside the NBA</a> "
            "they usually use lesser known players, here you have all of "
            "them. I'm thinking about adding a <em>hard mode</em> with only "
            "the weird ones for those looking for a challenge."
        },
        {
            'id': "scores",
            'question': "How are scores calculated?",
            'answer': "<code>(3*correct_guesses - wrong_guesses)</code> "
            "where <code>wrong_guesses</code> include not only the ones you "
            "didn't guess right, but also the rounds you did not play.<br />"

            "<strike>It's a work in progress, so it can change anytime. "
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
            "you'll get a score of 0.</strike>"
        },
        {
            'id': 'roster',
            'question': "How updated are the rosters?",
            'answer': "They are updated as of " + last_roster_update
        },
        {
            'id': 'shoutouts',
            'question': "Shout-outs",
            'answer': "For helping me with tips, testing, and more, "
            "shout-outs to Jess, SR, Alex Ntale, German, Duckie and Mora"
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

    # If, for some reason, we don't have a last_roster_update date, we delete
    # the question entirely
    if not last_roster_update:
        for q in questions:
            if q['id'] == 'roster':
                questions.remove(q)
                break

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

    guesses = get_guesses(code)

    return render(request, 'results.html', {
        'guesses': guesses, 'score': score, 'result': result,
        'parsed_code': parsed_code,
    })


def get_scoreboard(qs):
    if not qs:
        return []
    # The limit to search players for score
    SOFT_LIMIT = 20
    # The limit after being sorted also by time left
    HARD_LIMIT = 10

    results = []
    users = []

    for r in qs:
        if r.user not in users:
            users.append(r.user)
            results.append(r)
        if len(results) > SOFT_LIMIT:
            break

    results = sorted(results, key=lambda x: x.parsed_code['time_left'],
                     reverse=True)
    results = sorted(results, key=lambda x: x.score, reverse=True)
    results = results[:HARD_LIMIT]
    return results


def scoreboard(request):
    results = Result.objects.all()[:100]
    scoreboard_global = get_scoreboard(results)

    last7 = Result.objects.filter(
        created__gte=timezone.now() - timedelta(days=7)
    )

    scoreboard_last7 = get_scoreboard(last7)

    return render(request, 'scoreboard.html', {
        'scoreboard_global': scoreboard_global,
        'scoreboard_last7': scoreboard_last7,
    })


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
