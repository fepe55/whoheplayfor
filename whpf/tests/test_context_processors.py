from django.test import TestCase
from django.utils import formats, timezone

from whpf.context_processors import last_roster_update
from whpf.models import Options


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
