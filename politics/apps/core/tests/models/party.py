# coding=utf-8
from ...models import Party, View
from django.test import TransactionTestCase


class PartyTestCase(TransactionTestCase):
    """Unit tests for :class:`Party`."""

    fixtures = ("core_test_data",)

    def test_get_views(self):
        """``get_views()`` should return the party's views."""
        party = Party.objects.get(pk=1)
        self.assertEqual(set(party.get_views()), {
            View.objects.get(pk=1),
            View.objects.get(pk=5),
        })

    def test_get_views_override(self):
        """If a sub-party has any overriding views, ``get_views()`` should
            return them instead of the parent party's views."""
        party = Party.objects.get(pk=3)
        self.assertEqual(set(party.get_views()), {
            View.objects.get(pk=1),
            View.objects.get(pk=7)
        })

    def test_get_views_inheritance(self):
        """Sub-parties should inherit the views of their parents, with those of
            closer parents overriding those of more distant parents."""
        party = Party.objects.get(pk=4)
        self.assertEqual(set(party.get_views()), {
            View.objects.get(pk=1),
            View.objects.get(pk=7)
        })
