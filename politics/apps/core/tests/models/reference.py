# coding=utf-8
from django.contrib.auth.models import User
from django.test import TestCase
from politics.apps.core.models import Reference, ReferenceVote, View


class ReferenceTestCase(TestCase):
    """Unit tests for :class:`Reference`."""

    fixtures = ["core_test_data"]

    def test_author_vote(self):
        """When a reference is created, a :class:`Vote` should automatically be
            cast on it from its author, archiving their old vote."""
        user = User.objects.get(pk=1)
        view = View.objects.get(pk=1)
        vote = view.get_vote_for_user(user)

        # A vote should automatically be cast for this.
        reference = Reference(author=user, stance=View.SUPPORT, text="",
                              url="http://d.com/", view=view)
        reference.save()

        new_vote = view.get_vote_for_user(user)
        self.assertNotEqual(new_vote, vote)
        self.assertEqual(new_vote.content_object, reference)

    def test_manager_not_archived(self):
        """The default manager's ``not_archived()`` method should return all
            non-archived references."""
        # Some archived references must exist for this test to make sense.
        expected = Reference.objects.filter(is_archived=False)
        self.assertTrue(expected.exists())

        actual = Reference.objects.not_archived()
        self.assertEqual(len(actual), len(expected))
        self.assertFalse(any(r.is_archived for r in actual))

    def test_score_archived_votes(self):
        """The reference's score shouldn't include archived votes."""
        reference = Reference.objects.get(pk=1)
        expected = ReferenceVote.objects.get_for_object(reference).count()
        self.assertEqual(reference.score, expected)
