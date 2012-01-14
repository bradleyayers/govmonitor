# coding=utf-8
from django.contrib.auth.models import User
from django.test import TestCase
from politics.apps.core.models import Reference, View, Vote


class ViewTestCase(TestCase):
    """Unit tests for :class:`View`."""

    fixtures = ["core_test_data"]

    def setUp(self):
        self.view = View.objects.get(pk=1)

    def test_get_vote_for_user(self):
        """``get_vote_for_user()`` should return a user's vote in the view."""
        vote = self.view.get_vote_for_user(User.objects.get(pk=1))
        self.assertEqual(Reference.objects.get(pk=1), vote.content_object)

    def test_get_vote_for_user_none(self):
        """``get_vote_for_user()`` should return ``None`` if the user hasn't
            cast a vote in the view."""
        self.assertIsNone(self.view.get_vote_for_user(User.objects.get(pk=2)))

    def test_withdraw_vote(self):
        """``withdraw_vote()`` should withdraw a user's vote."""
        user = User.objects.get(pk=1)
        vote = self.view.get_vote_for_user(user)
        self.view.withdraw_vote(user)

        # The vote should have been archived.
        vote = Vote.objects.get(pk=vote.pk)
        self.assertTrue(vote.is_archived)

    def test_cast_vote(self):
        """``cast_vote()`` should withdraw a user's vote and cast another."""
        reference = Reference.objects.get(pk=2)
        user = User.objects.get(pk=1)
        vote = self.view.get_vote_for_user(user)
        self.view.cast_vote(reference, user)

        # The vote should have been archived...
        vote = Vote.objects.get(pk=vote.pk)
        self.assertTrue(vote.is_archived)

        # ...and a new one created.
        vote = self.view.get_vote_for_user(user)
        self.assertIsNotNone(vote)
        self.assertEqual(vote.content_object, reference)
