# coding=utf-8
from ...forms import PartyForm
from ...models import Party
from django.test.client import Client
from django.test import TransactionTestCase


class PartyFormTestCase(TransactionTestCase):
    """Unit tests for :class:`PartForm`."""

    fixtures = ("core_test_data",)

    def setUp(self):
        self.party = Party.objects.get(pk=1)

    def test_parent_self(self):
        """The form should be invalid if the parent is the Party we're
            editing."""
        form = PartyForm(instance=self.party, data={
            "name": self.party.name,
            "parent": self.party.pk
        })

        self.assertFalse(form.is_valid())

    def test_parent_loop(self):
        """The form should be invalid if setting the Party's parent to the given
            value would introduce a loop in the hierarchy."""
        # Party 3 is a child of party 1.
        form = PartyForm(instance=self.party, data={
            "name": self.party.name,
            "parent": 3
        })

        self.assertFalse(form.is_valid())