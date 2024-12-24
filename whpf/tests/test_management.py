from io import StringIO
from unittest.mock import Mock, patch

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase

from whpf.models import Conference, Player, Result
from whpf.tests.utils import mocked_get_players_api, mocked_get_players_api_empty


def mocked_requests_get(*args, **kwargs):
    """Basic requests.get mock"""
    mock = Mock()
    mock.status_code = 200
    return mock


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
