# coding=utf-8
from ..models import Party, View


class ViewManager(object):
    """A manager for retrieving :class:`View`s."""

    def get_view(self, issue, party, saved=False):
        """Retrieves a view.

        If no matching view is found in the database, one will be created. If
        you require the view to be saved (e.g. if it is to be referenced by a
        foreign key), pass ``saved=True`` and it is guaranteed to be saved.

        :param issue: The issue.
        :type  issue: ``politics.apps.core.models.Issue``
        :param party: The party.
        :type  party: ``politics.apps.core.models.Party``
        :param saved: Whether the returned view should be saved.
        :type  saved: ``boolean``
        :returns: The view corresponding to the given issue and party.
        :rtype: ``politics.apps.core.models.View``
        """
        try:
            return View.objects.get(issue=issue, party=party)
        except View.DoesNotExist:
            view = View(issue=issue, party=party)

            if saved:
                view.save()

            return view

    def get_views_for_issue(self, issue):
        """Retrieves all parties' views on an issue.

        If a party has no matching view in the database, one will be created.

        :param issue: The issue.
        :type  issue: ``politics.apps.core.models.Issue``
        :returns: All parties' views on ``issue``.
        :rtype: *Iterable* of ``politics.apps.core.models.View``
        """
        views = View.objects.filter(issue=issue)
        parties = set(Party.objects.all()) - {v.party for v in views}
        return list(views) + [View(issue=issue, party=p) for p in parties]