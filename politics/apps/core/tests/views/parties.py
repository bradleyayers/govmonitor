# coding=utf-8
from ...models import Party
from django.test.client import Client
from django.test import TransactionTestCase


class PartyViewsTestCase(TransactionTestCase):
    """Unit tests for :class:`Party` views."""

    fixtures = ("core_test_data",)

    def setUp(self):
        self.client = Client()
        self.client.login(username="chris", password="password")
        self.party = Party.objects.get(pk=1)

    def test_edit(self):
        """The edit view should update an existing :class:`Party`."""
        expected = "Updated Party!"
        party_count = Party.objects.count()
        response = self.client.post("/parties/1/edit/", {
            "name": expected
        })

        self.assertEqual(party_count, Party.objects.count())
        self.assertEqual(expected, Party.objects.get(pk=self.party.pk).name)