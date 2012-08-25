# coding=utf-8
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import TransactionTestCase
from politics.apps.core.models import Reference, View
from politics.apps.votes.models import Vote


class ViewTestCase(TransactionTestCase):
    """Unit tests for :class:`View`."""

    fixtures = ("core_test_data",)

    def setUp(self):
        self.view = View.objects.get(pk=1)

    def test_no_valid_references_is_unknown(self):
        """If a view has no references with score above 0.5, its stance should
            be unknown."""
        # Save the reference to force stance calculation.
        Reference.objects.get(pk=1).save()
        self.assertEqual(View.UNKNOWN, View.objects.get(pk=1).stance)

    def test_valid_reference(self):
        """A view's stance should be equal to that of its most recently
            published, valid reference (valid if its score is >= 0.5)."""
        for reference_pk in (1, 2):
            reference = Reference.objects.get(pk=reference_pk)

            for user_pk in (1, 2, 3):
                user = User.objects.get(pk=user_pk)
                vote = Vote(author=user, content_object=reference, type=Vote.UP)

                # We attempt to create a couple of votes that are already in the
                # fixture. Catch the error and continue because they're there.
                try:
                    vote.save()
                except IntegrityError:
                    pass

        # Both references are valid, but the oppose one was published later.
        view = View.objects.get(pk=1)
        self.assertEqual(View.OPPOSE, view.stance)
        self.assertEqual(Reference.objects.get(pk=2),
                view.get_current_reference())

        # If the score of the currently winning reference dips back below 0.5
        # (making it "invalid"), the view's stance should update accordingly.
        Vote.objects.filter(object_id=2).delete()
        view = View.objects.get(pk=1)
        self.assertEqual(View.SUPPORT, view.stance)
        self.assertEqual(Reference.objects.get(pk=1),
                view.get_current_reference())

        # ...and if all the references become invalid, it should become unknown.
        Vote.objects.all().delete()
        view = View.objects.get(pk=1)
        self.assertEqual(View.UNKNOWN, view.stance)
        self.assertEqual(None, view.get_current_reference())
