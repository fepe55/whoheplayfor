from django.apps import apps
from django.urls import reverse
from django.test import TestCase

from django.utils import timezone

from unittest.mock import patch

from whpf.apps import WhpfConfig
from whpf.models import Team, Options
from whpf.helpers import start_data
from whpf.context_processors import last_roster_update


class BaseTestCase(TestCase):
    fixtures = ['startdata.json']


class BasicAccessTestCase(BaseTestCase):
    def _test_url(self, url, expected_status_code=200):
        """Helper function for testing url"""
        response = self.client.get(url)
        self.assertEqual(response.status_code, expected_status_code)

    def test_home(self):
        """Test home view"""
        url = reverse('whpf:home')
        self._test_url(url)

    def test_tv(self):
        """Test TV view"""
        url = reverse('whpf:tv')
        self._test_url(url)

    def test_faq(self):
        """Test FAQ view"""
        url = reverse('whpf:faq')
        self._test_url(url)

    def test_scoreboard(self):
        """Test scoreboard view"""
        url = reverse('whpf:scoreboard')
        self._test_url(url)

    def test_stats(self):
        """Test stats view"""
        url = reverse('whpf:stats')
        self._test_url(url)

    def test_teams_stats(self):
        """Test teams stats view"""
        teams = Team.objects.all()
        for team in teams:
            url = team.stats_url()
            self._test_url(url)


class AppsTestCase(TestCase):
    def test_apps(self):
        """Test apps.py"""
        self.assertEqual(WhpfConfig.name, 'whpf')
        self.assertEqual(apps.get_app_config('whpf').name, 'whpf')


def mocked_get_players_api():
    return [
        [
            1630173, 'Achiuwa', 'Precious', 'precious-achiuwa', 1610612761,
            'raptors', 0, 'Toronto', 'Raptors', 'TOR', '5', 'F', '6-8', '225',
            'Memphis', 'Nigeria', 2020, 1, 20, 1.0, '2020', '2021', None, None,
            None, 'Season'
        ], [
            203500, 'Adams', 'Steven', 'steven-adams', 1610612763, 'grizzlies',
            0, 'Memphis', 'Grizzlies', 'MEM', '12', 'C', '6-11', '265',
            'Pittsburgh', 'New Zealand', 2013, 1, 12, 1.0, '2013', '2021',
            None, None, None, 'Season'
        ], [
            1628389, 'Adebayo', 'Bam', 'bam-adebayo', 1610612748, 'heat', 0,
            'Miami', 'Heat', 'MIA', '13', 'C-F', '6-9', '255', 'Kentucky',
            'USA', 2017, 1, 14, 1.0, '2017', '2021', None, None, None,
            'Season'
        ], [
            1628960, 'Allen', 'Grayson', 'grayson-allen', 1610612749, 'bucks',
            0, 'Milwaukee', 'Bucks', 'MIL', '7', 'G', '6-4', '198', 'Duke',
            'USA', 2018, 1, 21, 1.0, '2018', '2021', None, None, None,
            'Season'
        ], [
            1630247, 'Alston Jr.', 'Derrick', 'derrick-alston-jr', 1610612762,
            'jazz', 0, 'Utah', 'Jazz', 'UTA', '10', 'F', '6-9', '188',
            'Boise State', 'USA', None, None, None, 1.0, '2021', '2021', None,
            None, None, 'Season'
        ], [
            2546, 'Anthony', 'Carmelo', 'carmelo-anthony', 1610612747,
            'lakers', 0, 'Los Angeles', 'Lakers', 'LAL', '7', 'F', '6-7',
            '238', 'Syracuse', 'USA', 2003, 1, 3, 1.0, '2003', '2021', None,
            None, None, 'Season'
        ]
    ]


class TestHelperStartData(TestCase):
    @patch('whpf.helpers.get_players_api', mocked_get_players_api)
    def test_start_data(self):
        start_data()


class TestContextProcessor(TestCase):
    def test_context_processor_without_options(self):
        last_roster_update(None)

    def test_context_processor_with_options(self):
        Options.objects.create(last_roster_update=timezone.now())
        last_roster_update(None)
