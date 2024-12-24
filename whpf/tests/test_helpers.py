from unittest.mock import patch

from django.test import TestCase

from whpf.helpers import get_score, get_teams_and_players_database, start_data
from whpf.models import Conference, Player
from whpf.tests.utils import mocked_get_players_api


class TestHelpers(TestCase):
    """Class for testing helper functions that don't require data."""

    @patch("whpf.helpers.get_players_api", mocked_get_players_api, spec_set=True)
    def test_start_data(self):
        start_data()
        east_qs = Conference.objects.filter(name="East")
        self.assertTrue(east_qs.exists())


class TestHelpersWithData(TestCase):
    """Class for testing helper functions that require data."""

    fixtures = ["startdata.json"]

    def test_get_teams_and_players_database(self):
        """Test get_teams_and_players_database from helpers.py"""
        game_info = {
            "limit_teams": "0",
            "hard_mode": False,
        }
        Player.objects.update(times_guessed_pct=90)
        least_guessed_player = Player.objects.get(id=55)
        least_guessed_player.times_guessed_pct = 20
        least_guessed_player.save()

        teams, players = get_teams_and_players_database(game_info)

        self.assertEqual(teams[0]["nba_id"], 1610612737)
        self.assertEqual(players[0]["nba_id"], 1630173)

        # If using hard mode, the first one should be least guessed player
        game_info["hard_mode"] = True
        teams, players = get_teams_and_players_database(game_info)

        self.assertEqual(players[0]["nba_id"], least_guessed_player.nba_id)

    def test_get_score(self):
        """Test get_score from helpers.py"""
        code = (
            "v001010000080600200200163052662600020160961610010115037370020347"
            "1383801629003555501628970666600201949515100202693484801630217636"
            "3016305434454002039246565016302573953016297266438002034866666016"
            "2777450500020309552520162773255550020273460530162897342420162963"
            "1373736326"
        )
        score = get_score(code)
        self.assertEqual(score, 40)

    def test_get_score_legacy(self):
        """Test get_score from helpers.py with a legacy code format"""
        code = (
            "1000001060020020016277745757002015634949002015804444002030786464"
            "0162619552520000220762620020232957570020232264640020356061610162"
            "6145505000203461515100204001525200202347404000201960616100201609"
            "4848016277465858002016014646002031076464001011144242000024495151"
            "58336493855596891144"
        )
        score = get_score(code)
        self.assertEqual(score, 30)

    def test_get_score_error(self):
        """Test get_score from helpers.py with an empty code string"""
        code = ""
        with self.assertRaisesMessage(IndexError, "out of range"):
            get_score(code)
