from django.test import TestCase
from django.urls import reverse

from whpf.models import Team


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
