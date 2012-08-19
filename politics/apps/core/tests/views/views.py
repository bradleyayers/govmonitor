# coding=utf-8
from ...models import Issue, Party
from django.core.urlresolvers import reverse
from django.test.client import Client
from django.test import TransactionTestCase


class ViewViewsTestCase(TransactionTestCase):
    """Unit tests for :class:`View` views."""

    fixtures = ("core_test_data",)

    def setUp(self):
        self.client = Client()
        self.client.login(username="chris", password="password")

    def test_show_not_created(self):
        """The show view should work when the ``View`` hasn't actually been
            created in the database."""
        issue = Issue.objects.get(pk=2)
        party = Party.objects.get(pk=4)
        response = self.client.get(reverse("core:issues:view", kwargs={
            "issue_pk": issue.pk,
            "issue_slug": issue.slug,
            "party_pk": party.pk,
            "party_slug": party.slug
        }))

        self.assertEqual(response.status_code, 200)