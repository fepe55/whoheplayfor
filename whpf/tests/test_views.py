import json
from http import HTTPStatus
from unittest import mock

import pytest
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from whpf.forms import LIMIT_TEAMS_CHOICES, ROUNDS_CHOICES, TIME_CHOICES, GameForm
from whpf.helpers import get_score
from whpf.models import Options, Play, PlaySetting, Result, Team
from whpf.views import _get_scoreboard


class BasicAccessTestCase(TestCase):
    """Class for testing that every url returns a 200 status code."""

    fixtures = ["startdata.json"]

    def _test_url(self, url, expected_status_code=HTTPStatus.OK):
        """Helper function for testing url"""
        response = self.client.get(url)
        self.assertEqual(response.status_code, expected_status_code)

    def test_home(self):
        """Test home view"""
        url = reverse("whpf:home")
        self._test_url(url)

    def test_tv(self):
        """Test TV view"""
        url = reverse("whpf:tv")
        self._test_url(url)

    def test_faq(self):
        """Test FAQ view"""
        url = reverse("whpf:faq")
        self._test_url(url)

    def test_faq_with_options(self):
        """Test FAQ view"""
        Options.objects.create(last_roster_update=timezone.now())
        url = reverse("whpf:faq")
        self._test_url(url)

    def test_scoreboard(self):
        """Test scoreboard view"""
        url = reverse("whpf:scoreboard")
        self._test_url(url)

    def test_stats(self):
        """Test stats view"""
        url = reverse("whpf:stats")
        self._test_url(url)

    def test_teams_stats(self):
        """Test teams stats view"""
        teams = Team.objects.all()
        for team in teams:
            url = team.stats_url()
            self._test_url(url)

    def test_results(self):
        """Test results view"""
        code = "v001010000000600020200020270443460162839544449224755947494"
        url = reverse("whpf:results", args=[code])
        self._test_url(url)


@pytest.mark.django_db
def test_home_get_request(client):
    response = client.get(reverse("whpf:home"))

    assert response.status_code == HTTPStatus.OK
    assert "home.html" in [t.name for t in response.templates]  # Check if the correct template is used

    # Check for correct context data
    assert "form" in response.context
    assert "players_guessed_wrong" in response.context
    assert "total_plays" in response.context

    form = response.context["form"]
    assert isinstance(form, GameForm)

    # Check if form has default values
    assert form.initial["time"] == TIME_CHOICES[2][0]  # 60
    assert form.initial["rounds"] == ROUNDS_CHOICES[1][0]  # 20
    assert form.initial["limit_teams"] == LIMIT_TEAMS_CHOICES[0][0]  # 'all'


@pytest.mark.django_db
def test_home_post_valid_data(client):
    data = {
        "time": 60,
        "rounds": 20,
        "limit_teams": "0",
        "shuffle_teams": False,
        "show_player_name": True,
        "hard_mode": False,
    }

    response = client.post(reverse("whpf:home"), data)

    assert response.status_code == HTTPStatus.OK
    assert "whpf.html" in [t.name for t in response.templates]

    # Verify the game info is in the context
    assert "game_info" in response.context
    assert response.context["game_info"]["time"] == 60
    assert response.context["game_info"]["rounds"] == 20
    assert response.context["game_info"]["limit_teams"] == "0"

    # Ensure Play and PlaySetting are created
    play = Play.objects.first()
    assert play is not None

    # Check if PlaySetting objects are created correctly
    for setting_name, setting_value in data.items():
        assert PlaySetting.objects.filter(play=play, name=setting_name, value=str(setting_value)).exists()


@pytest.mark.django_db
def test_home_post_invalid_game_choices(client):
    data = {
        "time": 1000,  # Invalid time, not in TIME_CHOICES
        "rounds": 100,  # Invalid round, not in ROUNDS_CHOICES
        "limit_teams": "invalid_choice",  # Invalid limit_teams choice
        "shuffle_teams": False,
        "show_player_name": True,
        "hard_mode": False,
    }

    response = client.post(reverse("whpf:home"), data)

    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_get_scoreboard_empty_queryset():
    """Test the case where the queryset is empty."""
    result = _get_scoreboard(Result.objects.none())  # Empty queryset
    assert result == []  # Should return an empty list


@pytest.mark.django_db
def test_get_scoreboard_single_user(results_fixture):
    """Test the case where all results belong to one user."""
    user_results = Result.objects.filter(user=results_fixture[0].user)  # Get results for the first user
    result = _get_scoreboard(user_results)

    # The best result for the user should be first (score 100, time_left 10)
    assert result == [results_fixture[0]]


@pytest.mark.parametrize("view_name", ["whpf:right_guess", "whpf:wrong_guess"])
def test_non_ajax_request_to_guess_view(client, view_name):
    """Test that a non-AJAX request raises an Http404."""

    # Make a regular (non-AJAX) request
    response = client.post(reverse(view_name, args=["1"]))

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.django_db
@pytest.mark.parametrize("view_name", ["whpf:right_guess", "whpf:wrong_guess"])
@mock.patch("whpf.views.request_is_ajax", return_value=True, spec_set=True)
def test_ajax_request_to_guess_view(request_is_ajax_mock, client, user, create_players, view_name):
    """Test that the guess views work for valid AJAX requests."""

    client.force_login(user)

    response = client.post(reverse(view_name, args=["1"]))

    request_is_ajax_mock.assert_called_once()
    assert response.status_code == HTTPStatus.OK

    # Check that the response content type is JSON
    assert response["Content-Type"] == "application/json"

    # Check the response JSON content
    response_data = json.loads(response.content)
    assert response_data["success"] is True


def test_non_ajax_request_to_save_view(client):
    """Test that a non-AJAX request raises an Http404."""

    # Make a regular (non-AJAX) request
    response = client.post(reverse("whpf:save", args=["somecode"]))

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.django_db
@mock.patch("whpf.views.request_is_ajax", return_value=True, spec_set=True)
def test_save_view(request_is_ajax_mock, client, user, code):
    client.force_login(user)
    response = client.post(reverse("whpf:save", args=[code]))
    request_is_ajax_mock.assert_called_once()
    assert response.status_code == HTTPStatus.OK

    result = Result.objects.get()
    assert result.user == user
    assert result.code == code


def test_non_ajax_request_to_score_view(client):
    """Test that a non-AJAX request raises an Http404."""

    # Make a regular (non-AJAX) request
    response = client.post(reverse("whpf:score", args=["somecode"]))

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.django_db
@mock.patch("whpf.views.request_is_ajax", return_value=True, spec_set=True)
def test_score_view_without_play(request_is_ajax_mock, client, code):
    session = client.session
    session["play_id"] = "123"
    session.save()
    response = client.post(reverse("whpf:score", args=[code]))
    request_is_ajax_mock.assert_called_once()
    assert response.status_code == HTTPStatus.OK

    assert {"score": get_score(code)} == response.json()


@pytest.mark.django_db
@mock.patch("whpf.views.request_is_ajax", return_value=True, spec_set=True)
def test_score_view_with_play(request_is_ajax_mock, client, user, code):
    play = Play.objects.create(player=user)
    client.force_login(user)
    session = client.session
    session["play_id"] = play.id
    session.save()
    assert play.code == ""
    assert play.finished is False
    assert play.score == 0
    response = client.post(reverse("whpf:score", args=[code]))
    request_is_ajax_mock.assert_called_once()
    assert response.status_code == HTTPStatus.OK

    play.refresh_from_db()
    assert play.code == code
    assert play.finished is True
    assert {"score": get_score(code)} == response.json()
