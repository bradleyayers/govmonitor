# coding=utf-8
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError
from django.test import TestCase
from politics.apps.core.models import Vote


class VoteTestCase(TestCase):
    """Unit tests for :class:`Vote`."""

    fixtures = ["core_test_data", "votes_test_data"]

    def test_duplicate_vote(self):
        """Attempting to create duplicate votes should raise an exception.

        A vote is deemed to be a duplicate if there exists a non-archived vote
        from the same user on the same object.
        """
        with self.assertRaises(IntegrityError):
            vote = Vote.objects.get_for_model(User)[0]
            Vote(content_object=vote.content_object, author=vote.author).save()

    def test_manager_get_for_model(self):
        """The default manager's ``get_for_model()`` method should return all
            votes that have been cast on instances of a particular model."""
        content_type = ContentType.objects.get_for_model(User)
        user_votes = Vote.objects.filter(content_type=content_type)
        self.assertTrue(user_votes.exists())

        # First test without archived votes...
        actual = Vote.objects.get_for_model(User)
        expected = user_votes.filter(is_archived=False)
        self.assertEqual(len(actual), len(expected))
        self.assertFalse(any(v.is_archived for v in actual))
        self.assertTrue(all(isinstance(v.content_object, User) for v in actual))

        # ...and again with archived votes.
        actual = Vote.objects.get_for_model(User, True)
        expected = user_votes
        self.assertEqual(len(actual), len(expected))
        self.assertTrue(any(v.is_archived for v in actual))
        self.assertTrue(all(isinstance(v.content_object, User) for v in actual))

    def test_manager_get_for_instance(self):
        """The default manager's ``get_for_instance()`` method should return
            all votes that have been cast on a particular model instance."""
        user = User.objects.get(pk=1)
        content_type = ContentType.objects.get_for_model(User)
        object_votes = Vote.objects.filter(content_type=content_type,
                                           object_id=user.pk)
        self.assertTrue(object_votes.exists())

        # First test without archived votes...
        actual = Vote.objects.get_for_instance(user)
        expected = object_votes.filter(is_archived=False)
        self.assertEqual(len(actual), len(expected))
        self.assertFalse(any(v.is_archived for v in actual))
        self.assertTrue(all(v.content_object == user for v in actual))

        # ...and again with archived votes.
        actual = Vote.objects.get_for_instance(user, True)
        expected = object_votes
        self.assertEqual(len(actual), len(expected))
        self.assertTrue(any(v.is_archived for v in actual))
        self.assertTrue(all(v.content_object == user for v in actual))

    def test_manager_not_archived(self):
        """The default manager's ``not_archived()`` method should return all
            votes that are not archived."""
        expected = Vote.objects.filter(is_archived=False)
        self.assertTrue(expected.exists())

        actual = Vote.objects.not_archived()
        self.assertEqual(len(actual), len(expected))
        self.assertFalse(any(v.is_archived for v in actual))
