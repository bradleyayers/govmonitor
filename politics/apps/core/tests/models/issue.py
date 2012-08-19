# coding=utf-8
from django.test import TransactionTestCase
from politics.apps.core.models import Issue


class IssueTestCase(TransactionTestCase):
    """Unit tests for :class:`Issue`."""

    fixtures = ("core_test_data",)

    def test_percentage_views_known_no_views(self):
        """``percentage_views_known`` should return 0 when there are no views
            associated with the issue in the database."""
        issue = Issue.objects.get(pk=3)
        self.assertEqual(0, issue.percentage_views_known)