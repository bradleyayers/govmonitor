# coding=utf-8
from ..models import Vote
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import TransactionTestCase
from politics.apps.core.models import Reference


class VoteTestCase(TransactionTestCase):
    """Unit tests for the ``Vote`` class."""

    fixtures = ("core_test_data",)

    def test_duplicate_vote(self):
        """A user may only have one non-archived vote on an object. Attempting
            to create another should fail."""
        user = User.objects.get(pk=1)
        reference = Reference.objects.get(pk=1)
        vote = Vote(author=user, content_object=reference, type=Vote.UP)
        self.assertRaises(IntegrityError, vote.save)

    def test_refresh_score(self):
        reference = Reference.objects.get(pk=1)
        Vote.refresh_score(Vote.objects.get_for_instance(reference)[0])

        reference = Reference.objects.get(pk=1)
        self.assertAlmostEqual(0.2686367, reference.score)

        # Create a down vote.
        user = User.objects.get(pk=2)
        vote = Vote(author=user, content_object=reference, type=Vote.DOWN)
        vote.save()

        reference = Reference.objects.get(pk=1)
        self.assertAlmostEqual(0.1203635, reference.score)

    def test_refresh_score_no_votes(self):
        user = User.objects.get(pk=1)
        reference = Reference.objects.get(pk=2)
        vote = Vote(author=user, content_object=reference, is_archived=True,
            type=Vote.UP)
        vote.save()
        Vote.refresh_score(vote)

        reference = Reference.objects.get(pk=2)
        self.assertEqual(0, reference.score)
