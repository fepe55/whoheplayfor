from io import StringIO
from unittest.mock import Mock, patch

from django.apps import apps
from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.utils import formats, timezone

from whpf.apps import WhpfConfig
from whpf.context_processors import last_roster_update
from whpf.helpers import get_score, get_teams_and_players_database, start_data
from whpf.models import Conference, Options, Player, Result, Team


class BasicAccessTestCase(TestCase):
    """Class for testing that every url returns a 200 status code."""

    fixtures = ["startdata.json"]

    def _test_url(self, url, expected_status_code=200):
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


class AppsTestCase(TestCase):
    """Class for testing apps.py."""

    def test_apps(self):
        """Test apps.py"""
        self.assertEqual(WhpfConfig.name, "whpf")
        self.assertEqual(apps.get_app_config("whpf").name, "whpf")


def mocked_requests_get(*args, **kwargs):
    """Basic requests.get mock"""
    mock = Mock()
    mock.status_code = 200
    return mock


def mocked_get_players_api():
    """Mocked get_players_api with a few examples.
    Including a wierd one with 0 as the fourth (zero-based) value
    """
    return [
        [
            1630173,
            "Achiuwa",
            "Precious",
            "precious-achiuwa",
            1610612761,
            "raptors",
            0,
            "Toronto",
            "Raptors",
            "TOR",
            "5",
            "F",
            "6-8",
            "225",
            "Memphis",
            "Nigeria",
            2020,
            1,
            20,
            1.0,
            "2020",
            "2021",
            None,
            None,
            None,
            "Season",
        ],
        [
            203500,
            "Adams",
            "Steven",
            "steven-adams",
            1610612763,
            "grizzlies",
            0,
            "Memphis",
            "Grizzlies",
            "MEM",
            "12",
            "C",
            "6-11",
            "265",
            "Pittsburgh",
            "New Zealand",
            2013,
            1,
            12,
            1.0,
            "2013",
            "2021",
            None,
            None,
            None,
            "Season",
        ],
        [
            1628389,
            "Adebayo",
            "Bam",
            "bam-adebayo",
            1610612748,
            "heat",
            0,
            "Miami",
            "Heat",
            "MIA",
            "13",
            "C-F",
            "6-9",
            "255",
            "Kentucky",
            "USA",
            2017,
            1,
            14,
            1.0,
            "2017",
            "2021",
            None,
            None,
            None,
            "Season",
        ],
        [
            1628960,
            "Allen",
            "Grayson",
            "grayson-allen",
            1610612749,
            "bucks",
            0,
            "Milwaukee",
            "Bucks",
            "MIL",
            "7",
            "G",
            "6-4",
            "198",
            "Duke",
            "USA",
            2018,
            1,
            21,
            1.0,
            "2018",
            "2021",
            None,
            None,
            None,
            "Season",
        ],
        [
            1630247,
            "Alston Jr.",
            "Derrick",
            "derrick-alston-jr",
            1610612762,
            "jazz",
            0,
            "Utah",
            "Jazz",
            "UTA",
            "10",
            "F",
            "6-9",
            "188",
            "Boise State",
            "USA",
            None,
            None,
            None,
            1.0,
            "2021",
            "2021",
            None,
            None,
            None,
            "Season",
        ],
        [
            2546,
            "Anthony",
            "Carmelo",
            "carmelo-anthony",
            1610612747,
            "lakers",
            0,
            "Los Angeles",
            "Lakers",
            "LAL",
            "7",
            "F",
            "6-7",
            "238",
            "Syracuse",
            "USA",
            2003,
            1,
            3,
            1.0,
            "2003",
            "2021",
            None,
            None,
            None,
            "Season",
        ],
        [
            2546,
            "Anthony",
            "Carmelo",
            "carmelo-anthony",
            1610612747,
            "lakers",
            0,
            "Los Angeles",
            "Lakers",
            "LAL",
            "7",
            "F",
            "6-7",
            "238",
            "Syracuse",
            "USA",
            2003,
            1,
            3,
            1.0,
            "2003",
            "2021",
            None,
            None,
            None,
            "Season",
        ],
        [None, None, None, None, 0],
    ]


def mocked_get_players_api_empty():
    """Mocked get_players_api with an empty return"""
    return []


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


class TestContextProcessor(TestCase):
    """Class for testing context processors."""

    def test_context_processor_without_options(self):
        """Test context processor without options"""
        last_update = last_roster_update(None)
        self.assertEqual(last_update["last_roster_update"], "")

    def test_context_processor_with_options(self):
        """Test context processor with options"""
        now = timezone.now()
        Options.objects.create(last_roster_update=now)
        last_update = last_roster_update(None)
        self.assertEqual(last_update["last_roster_update"], formats.date_format(now, "F jS, Y"))


class TestManagementCommands(TestCase):
    """Class for testing management command that don't require data."""

    @patch("whpf.helpers.get_players_api", mocked_get_players_api, spec_set=True)
    def test_start_data(self):
        """Test start_data management command"""
        east_qs = Conference.objects.filter(name="East")
        self.assertFalse(east_qs.exists())
        call_command("startdata")
        east_qs = Conference.objects.filter(name="East")
        self.assertTrue(east_qs.exists())

    @patch("whpf.management.commands.update_rosters.get_players_api", mocked_get_players_api_empty, spec_set=True)
    def test_update_rosters_without_players(self):
        """Test update_rosters management command"""
        # Starting set based on fixture
        out = StringIO()
        call_command("update_rosters", stdout=out)
        stdout = out.getvalue()
        self.assertIn("Starting at", stdout)
        self.assertIn("Getting all the players from the API", stdout)
        # If get_players_api is empty, we assume NBA.com issue
        self.assertIn("Error with NBA.com", stdout)


class TestManagementCommandsWithData(TestCase):
    """Class for testing management command that require data."""

    fixtures = ["startdata.json"]

    def test_recalculate_scores(self):
        """Test recalculate scores management command"""
        code = (
            "v001010000080600200200163052662600020160961610010115037370020347"
            "1383801629003555501628970666600201949515100202693484801630217636"
            "3016305434454002039246565016302573953016297266438002034866666016"
            "2777450500020309552520162773255550020273460530162897342420162963"
            "1373736326"
        )
        user = User.objects.create_user("john", "lennon@thebeatles.com", "pwd")

        result = Result.objects.create(code=code, user=user)
        self.assertEqual(result.score, 0)
        call_command("recalculate_scores")
        result.refresh_from_db()
        self.assertEqual(result.score, 40)

    @patch("whpf.management.commands.update_rosters.get_players_api", mocked_get_players_api, spec_set=True)
    @patch("requests.get", mocked_requests_get, spec_set=True)
    @patch("time.sleep", spec_set=True)
    def test_update_rosters(self, mock_sleep):
        """Test update_rosters management command"""
        # Starting set based on fixture
        self.assertEqual(Player.objects.count(), 587)

        out = StringIO()
        call_command("update_rosters", stdout=out)
        stdout = out.getvalue()
        self.assertIn("Starting at", stdout)
        self.assertIn("Started", stdout)
        self.assertIn("Ended", stdout)
        self.assertIn("Elapsed", stdout)
        self.assertIn("has a face", stdout)

        # After updating the rosters, everyone should be marked as inactive except the valid 6 from the mocked API call
        self.assertEqual(Player.objects.count(), 6)

    @patch("whpf.management.commands.update_rosters.get_players_api", mocked_get_players_api, spec_set=True)
    def test_update_rosters_without_faceless_check(self):
        """Test update_rosters management command without
        faceless check
        """
        # Starting set based on fixture
        self.assertEqual(Player.objects.count(), 587)

        out = StringIO()
        call_command("update_rosters", no_faceless_check=True, stdout=out)
        stdout = out.getvalue()
        self.assertIn("Starting at", stdout)
        self.assertIn("Started", stdout)
        self.assertIn("Ended", stdout)
        self.assertIn("Elapsed", stdout)
        self.assertNotIn("Has a face", stdout)

        # After updating the rosters, everyone should be marked as inactive except the valid 6 from the mocked API call
        self.assertEqual(Player.objects.count(), 6)
