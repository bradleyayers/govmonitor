# coding=utf-8
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError
from django.test import TestCase
from politics.apps.core.models import Reference, ReferenceVote, View


class ReferenceVoteTestCase(TestCase):
    """Unit tests for :class:`ReferenceVote`."""

    fixtures = ["core_test_data"]

    def test_duplicate_vote(self):
        """Attempting to create a duplicate vote should raise an exception.

        A vote is deemed to be a duplicate if there exists a non-archived vote
        from the same user on any reference in the view.
        """
        with self.assertRaises(IntegrityError):
            ReferenceVote(content_object=Reference.objects.get(pk=2),
                          author=User.objects.get(pk=1)).save()

    def test_manager_get_for_view(self):
        """The default manager's ``get_for_view()`` method should return all
            votes that have been cast on references in a particular view."""
        view = View.objects.get(pk=1)
        votes = ReferenceVote.objects.filter(
                content_type=ContentType.objects.get_for_model(Reference),
                object_id__in=[r.pk for r in view.reference_set.all()])

        # First, test without archived votes...
        actual = ReferenceVote.objects.get_for_view(view)
        expected = votes.filter(is_archived=False)
        self.assertEqual(len(actual), len(expected))
        self.assertFalse(any(v.is_archived for v in actual))
        self.assertTrue(all(v.content_object.view == view for v in actual))

        # ...and again with archived votes.
        actual = ReferenceVote.objects.get_for_view(view, True)
        expected = votes
        self.assertEqual(len(actual), len(expected))
        self.assertTrue(any(v.is_archived for v in actual))
        self.assertTrue(all(v.content_object.view == view for v in actual))
