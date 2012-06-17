# coding=utf-8
from django.test.client import Client
from django.test import TransactionTestCase


class ReferenceViewsTestCase(TransactionTestCase):
    """Unit tests for :class:`Reference` views."""

    fixtures = ("core_test_data",)

    def setUp(self):
        self.client = Client()
        self.client.login(username="chris", password="password")

    def test_votes_invalid_pk(self):
        """The ``votes`` view should return 404 Not Found if the primary key
            container in the URL is invalid."""
        response = self.client.post("/references/1337/votes/")
        self.assertEquals(404, response.status_code)
