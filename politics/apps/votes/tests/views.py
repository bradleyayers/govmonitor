# coding=utf-8
from ..models import Vote
from ..views import votes
from django.contrib.auth.models import AnonymousUser, User
from django.test import TransactionTestCase
import fudge
from politics.apps.core.models import Reference


class VotesViewTestCase(TransactionTestCase):
    """Unit tests for the generic ``votes`` view."""

    fixtures = ("core_test_data",)

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.vote_count = Vote.objects.count()

    def test_delete(self):
        """Making a DELETE request should archive the user's current vote on the
            object and return 200 OK."""
        request = fudge.Fake("HttpRequest").has_attr(
            method="DELETE",
            user=self.user
        )

        reference = Reference.objects.get(pk=1)
        old_vote = Vote.objects.get_for_instance(reference)
        old_vote = old_vote.filter(author=self.user)[0]

        response = votes(request, reference)
        self.assertEqual(200, response.status_code)
        self.assertTrue(Vote.objects.get(pk=old_vote.pk).is_archived)

    def test_get(self):
        """Making a GET request should return 405 Method Not Allowed."""
        request = fudge.Fake("HttpRequest").has_attr(
            method="GET",
            path="/",
            user=self.user
        )

        response = votes(request, self.user)
        self.assertEqual(405, response.status_code)

    def test_not_authenticated(self):
        """Attempting to create/delete a vote when not authenticated should
            fail, returning 401 Unauthorized."""
        request = fudge.Fake("HttpRequest").has_attr(
            method="POST",
            POST={"type": Vote.UP},
            user=AnonymousUser()
        )

        response = votes(request, self.user)
        self.assertEqual(401, response.status_code)
        self.assertEqual(self.vote_count, Vote.objects.count())

    def test_post(self):
        """Making a valid POST request should archive the user's current vote on
            the object, create a new vote, and return 200 OK."""
        request = fudge.Fake("HttpRequest").has_attr(
            method="POST",
            POST={"type": Vote.DOWN},
            user=self.user
        )

        # Fetch the user's current vote.
        reference = Reference.objects.get(pk=1)
        old_vote = Vote.objects.get_for_instance(reference)
        old_vote = old_vote.filter(author=self.user)[0]

        response = votes(request, reference)
        self.assertEqual(201, response.status_code)
        self.assertEqual(self.vote_count + 1, Vote.objects.count())
        self.assertTrue(Vote.objects.get(pk=old_vote.pk).is_archived)

        vote = Vote.objects.latest("pk")
        self.assertEqual(vote.author, self.user)
        self.assertEqual(vote.content_object, reference)
        self.assertEqual(vote.type, Vote.DOWN)

    def test_post_fields(self):
        """Fields other than `type` should be ignored."""
        request = fudge.Fake("HttpRequest").has_attr(
            method="POST",
            POST={"is_archived": True, "type": Vote.UP},
            user=self.user
        )

        response = votes(request, self.user)
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

        response = votes(request, self.user)
        self.assertEqual(400, response.status_code)
        self.assertEqual(self.vote_count, Vote.objects.count())
