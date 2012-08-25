# coding=utf-8
from django.test import TransactionTestCase
from politics.apps.core.models import Issue, Party


class IssueTestCase(TransactionTestCase):
    """Unit tests for :class:`Issue`."""

    fixtures = ("core_test_data",)

    def test_percentage_views_known(self):
        """``percentage_views_known`` should return the percentage of views on
            the issue that are known."""
        issue = Issue.objects.get(pk=4)
        self.assertAlmostEqual(100.0 / 3, issue.percentage_views_known)

    def test_percentage_views_known_no_parties(self):
        """```percentage_views_known`` should return 0 when there are no parties
            in the database."""
        Party.objects.all().delete()
        self.assertEqual(0, Issue.objects.get(pk=1).percentage_views_known)

    def test_percentage_views_known_no_views(self):
        """``percentage_views_known`` should return 0 when there are no views
            associated with the issue in the database."""
        self.assertEqual(0, Issue.objects.get(pk=3).percentage_views_known)