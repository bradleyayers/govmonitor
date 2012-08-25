# coding=utf-8
from django.test import TransactionTestCase
from politics.apps.core.models import Issue, Party


class PartyTestCase(TransactionTestCase):
    """Unit tests for :class:`Party`."""

    fixtures = ("core_test_data",)

    def test_percentage_views_known(self):
        """``percentage_views_known`` should return the percentage of the
            party's views that are known."""
        self.assertEqual(75, Party.objects.get(pk=1).percentage_views_known)

    def test_percentage_views_known_no_issues(self):
        """``percentage_views_known`` should return 0 when there are no issues
            in the database."""
        Issue.objects.all().delete()
        self.assertEqual(0, Party.objects.get(pk=1).percentage_views_known)

    def test_percentage_views_known_no_views(self):
        """``percentage_views_known`` should return 0 when there are no views
            associated with the party in the database."""
        self.assertEqual(0, Party.objects.get(pk=5).percentage_views_known)