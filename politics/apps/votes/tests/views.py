# coding=utf-8
from ..models import Vote
from ..views import votes
from django.contrib.auth.models import AnonymousUser, User
from django.test import TransactionTestCase
import fudge
import json
from politics.apps.core.models import Reference


class VotesViewTestCase(TransactionTestCase):
    """Unit tests for the generic ``votes`` view."""

    fixtures = ("core_test_data",)

    def setUp(self):
        self.reference = Reference.objects.get(pk=1)
        self.user = User.objects.get(pk=1)
        self.vote_count = Vote.objects.count()

    def test_delete(self):
        """Making a DELETE request should archive the user's current vote on the
            object (if any), update the object's score, and return 200 OK."""
        request = fudge.Fake("HttpRequest").has_attr(
            method="DELETE",
            user=self.user
        )

        old_vote = Vote.objects.get_for_instance(self.reference)
        old_vote = old_vote.filter(author=self.user)[0]
        self.assertNotEqual(0, self.reference.score)

        response = votes(request, self.reference)
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, json.loads(response.content)["score"])
        self.assertTrue(Vote.objects.get(pk=old_vote.pk).is_archived)
        self.assertEqual(0, Reference.objects.get(pk=self.reference.pk).score)

    def test_get(self):
        """Making a GET request should return 405 Method Not Allowed."""
        request = fudge.Fake("HttpRequest").has_attr(
            method="GET",
            path="/",
            user=self.user
        )

        response = votes(request, self.reference)
        self.assertEqual("", response.content)
        self.assertEqual(405, response.status_code)

    def test_not_authenticated(self):
        """Making a DELETE/POST request when not authenticated should return
            401 Unauthorized."""
        request = fudge.Fake("HttpRequest").has_attr(
            method="POST",
            POST={"type": Vote.UP},
            user=AnonymousUser()
        )

        response = votes(request, self.reference)
        self.assertEqual("", response.content)
        self.assertEqual(401, response.status_code)
        self.assertEqual(self.vote_count, Vote.objects.count())

    def test_post(self):
        """Making a POST request should archive the user's current vote on the
            object, create a new vote, update its score, and return 200 OK."""
        request = fudge.Fake("HttpRequest").has_attr(
            method="POST",
            POST={"type": Vote.UP},
            user=self.user
        )

        old_vote = Vote.objects.get_for_instance(self.reference)
        old_vote = old_vote.filter(author=self.user)[0]
        self.assertAlmostEqual(0.2686367, self.reference.score)

        # The user's current vote should be archived but, because they had
        # already voted this reference up, its score shouldn't change.
        response = votes(request, self.reference)
        self.assertEqual(201, response.status_code)
        self.assertEqual(self.vote_count + 1, Vote.objects.count())
        self.assertTrue(Vote.objects.get(pk=old_vote.pk).is_archived)
        self.assertAlmostEqual(0.2686367, json.loads(response.content)["score"])
        self.assertAlmostEqual(0.2686367,
            Reference.objects.get(pk=self.reference.pk).score)

        vote = Vote.objects.latest("pk")
        self.assertEqual(vote.author, self.user)
        self.assertEqual(vote.content_object, self.reference)
        self.assertEqual(vote.type, Vote.UP)

        # The reference's score should increase if another user votes it up.
        request.user = User.objects.get(pk=2)
        response = votes(request, self.reference)
        self.assertAlmostEqual(0.4235045, json.loads(response.content)["score"])
        self.assertAlmostEqual(0.4235045,
            Reference.objects.get(pk=self.reference.pk).score)

    def test_post_fields(self):
        """Fields other than `type` should be ignored."""
        request = fudge.Fake("HttpRequest").has_attr(
            method="POST",
            POST={"is_archived": True, "type": Vote.UP},
            user=self.user
        )

        response = votes(request, self.reference)
        self.assertEqual(201, response.status_code)
        self.assertEqual(self.vote_count + 1, Vote.objects.count())
        self.assertFalse(Vote.objects.latest("pk").is_archived)

    def test_post_invalid(self):
        """Making an invalid POST request should return 400 Bad Request."""
        request = fudge.Fake("HttpRequest").has_attr(
            method="POST",
            POST={},
            user=self.user
        )

        response = votes(request, self.reference)
        self.assertEqual("", response.content)
        self.assertEqual(400, response.status_code)
        self.assertEqual(self.vote_count, Vote.objects.count())
