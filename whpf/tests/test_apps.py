from django.apps import apps
from django.test import TestCase

from whpf.apps import WhpfConfig


class AppsTestCase(TestCase):
    """Class for testing apps.py."""

    def test_apps(self):
        """Test apps.py"""
        self.assertEqual(WhpfConfig.name, "whpf")
        self.assertEqual(apps.get_app_config("whpf").name, "whpf")
