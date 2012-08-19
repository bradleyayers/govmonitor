# coding=utf-8
from ...managers import ViewManager
from ...models import Issue, Party, View
from django.test import TransactionTestCase


class ViewManagerTestCase(TransactionTestCase):
    """Tests for ``politics.apps.core.managers.ViewManager``."""

    fixtures = ("core_test_data",)

    def setUp(self):
        self.view_manager = ViewManager()

    def test_get_view(self):
        """``get_view()`` should return the corresponding to the given issue and
            party."""
        issue = Issue.objects.get(pk=1)
        party = Party.objects.get(pk=1)
        view = self.view_manager.get_view(issue, party)
        self.assertEqual(View.objects.get(pk=1), view)

    def test_get_view_nonexistent(self):
        """``get_view()`` should return an unsaved view if there's no matching
            view in the database."""
        issue = Issue.objects.get(pk=2)
        party = Party.objects.get(pk=4)
        view = self.view_manager.get_view(issue, party)
        self.assertEqual(view.UNKNOWN, view.stance)
        self.assertIsNone(view.pk)

    def test_get_view_saved(self):
        """```get_view()`` should create a view if no matching view is found and
            ``saved=True`` is passed."""
        issue = Issue.objects.get(pk=2)
        party = Party.objects.get(pk=4)
        self.assertEqual(0, len(View.objects.filter(issue=issue, party=party)))

        view_count = View.objects.count()
        view = self.view_manager.get_view(issue, party, saved=True)
        self.assertEquals(view_count + 1, View.objects.count())
        self.assertIsNotNone(view.pk)

    def test_get_views_for_issue(self):
        """``get_views_for_issue()`` should return all parties' views on the
            given issue, creating views for any not present in the database."""
        issue = Issue.objects.get(pk=2)
        views = self.view_manager.get_views_for_issue(issue)

        self.assertEqual(Party.objects.count(), len(views))
        self.assertEqual({view.party for view in views},
                set(Party.objects.all()))

        for party in Party.objects.all():
            view = next(view for view in views if view.party == party)
            self.assertEqual(issue, view.issue)

            try:
                db_view = View.objects.get(issue=issue, party=party)
                self.assertEqual(db_view, view)
            except View.DoesNotExist:
                self.assertEqual(View.UNKNOWN, view.stance)