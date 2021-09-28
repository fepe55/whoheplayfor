from django.test import TestCase
from django.urls import reverse

from whpf.models import Team
from whpf.helpers import start_data


class BaseTestCase(TestCase):
    def setUp(self):
        #  https://docs.djangoproject.com/en/2.2/ref/contrib/staticfiles/#manifeststaticfilesstorage
        #  self.storage = 'django.contrib.staticfiles.storage.StaticFilesStorage'  # noqa:E501
        start_data()


class BasicAccessTestCase(BaseTestCase):
    def _test_url(self, url, expected_status_code=200):
        response = self.client.get(url)
        self.assertEqual(response.status_code, expected_status_code)

    def test_home(self):
        url = reverse('whpf:home')
        self._test_url(url)

    def test_tv(self):
        url = reverse('whpf:tv')
        self._test_url(url)

    def test_faq(self):
        url = reverse('whpf:faq')
        self._test_url(url)

    def test_scoreboard(self):
        url = reverse('whpf:scoreboard')
        self._test_url(url)

    def test_stats(self):
        url = reverse('whpf:stats')
        self._test_url(url)

    def test_teams_stats(self):
        teams = Team.objects.all()
        for team in teams:
            url = team.stats_url()
            self._test_url(url)
