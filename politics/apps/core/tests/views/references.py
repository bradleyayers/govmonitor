# coding=utf-8
from django.contrib.auth.models import User
from django.test.client import Client
from django.test import TestCase
import json
from politics.apps.core.models import Reference, ReferenceVote, View


class ReferenceViewsTestCase(TestCase):
    """Unit tests for :class:`Reference` views."""

    fixtures = ["core_test_data"]

    def setUp(self):
        self.client = Client()

    def test_votes_create(self):
        """Making a POST request to the ``votes`` view should archive the
            user's existing vote in the :class:`View` and create a new one."""
        self.client.login(username="chris", password="password")
        response = self.client.post("/references/2/votes/")

        # The old vote should have been archived, reducing the score of the
        # first reference, and a new vote should have been created.
        view = View.objects.get(pk=1)
        self.assertEqual(1, ReferenceVote.objects.get_for_view(view).count())
        self.assertEqual(0, Reference.objects.get(pk=1).score)
        self.assertEqual(1, Reference.objects.get(pk=2).score)
        self.assertEqual(200, response.status_code)
        self.assertEqual({"score": Reference.objects.get(pk=2).score},
                         json.loads(response.content))

    def test_votes_delete(self):
        """Making a DELETE request to the ``votes`` view should archive the
            user's current vote in the :class:`View` (if any)."""
        # The user must have cast at least one vote on the view.
        votes = ReferenceVote.objects.get_for_view(View.objects.get(pk=1))
        votes = votes.filter(author=User.objects.get(pk=1))
        self.assertTrue(votes.exists())

        self.client.login(username="chris", password="password")
        response = self.client.delete("/references/1/votes/")

        self.assertFalse(votes.exists())
        self.assertEqual(200, response.status_code)
        self.assertEqual({"score": Reference.objects.get(pk=1).score},
                         json.loads(response.content))

    def test_votes_invalid_pk(self):
        """The ``votes`` view should return 404 Not Found if the primary key
            container in the URL is invalid."""
        self.client.login(username="chris", password="password")
        response = self.client.post("/references/1337/votes/")
        self.assertEquals(404, response.status_code)

    def test_votes_not_authenticated(self):
        """The ``votes`` view should return 401 Unauthorized if the requesting
            user isn't logged in."""
        response = self.client.post("/references/1/votes/")
        self.assertEquals(401, response.status_code)
