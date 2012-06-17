# coding=utf-8
from django.contrib.auth.models import AnonymousUser, User
from django.test import TransactionTestCase
from politics.apps.core.models import Reference, View
from politics.apps.votes.models import Vote


class ViewTestCase(TransactionTestCase):
    """Unit tests for :class:`View`."""

    fixtures = ("core_test_data",)

    def setUp(self):
        self.view = View.objects.get(pk=1)
