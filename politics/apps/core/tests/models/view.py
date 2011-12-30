# coding=utf-8
from django.contrib.auth.models import User
from django.test import TestCase
from politics.apps.core.models import Reference, View


class ViewTestCase(TestCase):
    """Unit tests for :class:`View`."""

    fixtures = ["core_test_data"]

    def test_get_vote_for_user(self):
        """``get_vote_for_user()`` should return a user's vote in the view."""
        view = View.objects.get(pk=1)
        vote = view.get_vote_for_user(User.objects.get(pk=1))
        self.assertEqual(Reference.objects.get(pk=1), vote.content_object)

    def test_get_vote_for_user_none(self):
        """``get_vote_for_user()`` should return ``None`` if the user hasn't
            cast a vote in the view."""
        view = View.objects.get(pk=1)
        self.assertIsNone(view.get_vote_for_user(User.objects.get(pk=2)))
