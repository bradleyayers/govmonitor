# coding=utf-8
from ...models import Issue
from django.core.urlresolvers import reverse
from django.test import TransactionTestCase
from django.test.client import Client


class IssueViewTestCase(TransactionTestCase):
    """Unit tests for :class:`Issue` views."""

    fixtures = ("core_test_data",)

    def setUp(self):
        self.client = Client()
        self.client.login(username="chris", password="password")

    def test_show_no_views(self):
        """The ``show`` view should work when the ``Issue`` doesn't have any
            associated views in the database."""
        issue = Issue.objects.get(pk=3)
        response = self.client.get(reverse("core:issues:show", kwargs={
            "issue_pk": issue.pk,
            "issue_slug": issue.slug
        }))

        self.assertEqual(response.status_code, 200)

    def test_new(self):
        response = self.client.get(reverse("core:issues:new"))
        self.assertEqual(response.status_code, 200)