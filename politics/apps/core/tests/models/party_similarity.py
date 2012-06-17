# coding=utf-8
from django.test import TransactionTestCase
from politics.apps.core.models import Party, PartySimilarity


class PartySimilarityTestCase(TransactionTestCase):
    """Unit tests for :class:`PartySimilarity`."""

    fixtures = ("core_test_data",)

    def test_invalid_similarity(self):
        """Invalid similarity values should be rejected."""
        party_similarity = PartySimilarity()
        party_similarity.first_party = Party.objects.get(pk=1)
        party_similarity.second_party = Party.objects.get(pk=2)

        party_similarity.similarity = -1
        self.assertRaises(ValueError, party_similarity.save)

        party_similarity.similarity = 2
        self.assertRaises(ValueError, party_similarity.save)
