# coding=utf-8
from autoslug.fields import AutoSlugField
from django.db import models
from itertools import groupby


def _get_view_slug(view):
    """Builds a view's slug."""
    from . import Issue, Party

    try:
        return "%s %s" % (view.party.name, view.issue.name)
    except (Issue.DoesNotExist, Party.DoesNotExist):
        return ""


class View(models.Model):
    """A political party's view on an issue.

    At the core of a ``View`` is the party's ``stance`` on the issue: oppose or
    support. For example, the Australian Labor Party supports the carbon tax;
    the Liberal Party of Australia, on the other hand, does not.
    """

    # Stances a party might take on an issue.
    # XXX: If you change these, update the `max_length` of fields.
    SUPPORT = "support"
    OPPOSE = "oppose"
    UNCLEAR = "unclear"
    UNKNOWN = "unknown"

    # Stance choices to be passed to model/form fields.
    SUPPORT_CHOICE = (SUPPORT, "Support")
    OPPOSE_CHOICE = (OPPOSE, "Oppose")
    UNCLEAR_CHOICE = (UNCLEAR, "Unclear")
    UNKNOWN_CHOICE = (UNKNOWN, "Unknown")

    # View stance choices.
    _STANCE_CHOICES = (
      SUPPORT_CHOICE,
      OPPOSE_CHOICE,
      UNCLEAR_CHOICE,
      UNKNOWN_CHOICE,
    )

    issue = models.ForeignKey("Issue")
    party = models.ForeignKey("Party")

    # Issue.name has a maximum length of 128 characters, while Party.name is
    # 64 characters. Add 1 for the space and we get a maximum length of 193.
    slug = AutoSlugField(always_update=True, populate_from=_get_view_slug,
                         max_length=193)

    # The party's apparent stance on the issue: the stance with the greatest
    # total `Reference` score. While this value could just be calculated, we
    # store it to make things nice and speed.
    stance = models.CharField(choices=_STANCE_CHOICES, default=UNKNOWN,
                              max_length=7)

    class Meta:
        app_label = "core"

    def __unicode__(self):
        return "%s, %s" % (self.party.name, self.issue.name)

    def get_vote_for_user(self, user):
        """Retrieve a user's vote within the view.

        :param user: The user whose vote is to be retrieved.
        :type  user: ``django.contrib.auth.models.User``
        :returns: ``user``'s vote in the view or ``None``
        :rtype: :class:`ReferenceVote` or ``None``
        """
        from . import ReferenceVote

        try:
            votes = ReferenceVote.objects.get_for_view(self)
            return votes.filter(author=user)[0]
        except IndexError:
            return None

    def refresh_stance(self):
        """Recalculate the view's ``stance``.

        A view's stance is equal to that of its best :class:`Reference`: the
        reference that currently has the greatest number of non-archived votes.

        Assumes that all the view's :class:`Reference`s are up to date (their
        scores reflect the votes that have been cast). If the stance changes,
        the :class:`Issue` is saved to touch its ``updated_at`` timestamp.
        """
        try:
            # Fetch the reference(s) with the greatest score.
            references = self.reference_set.order_by("-score")
            references = list(groupby(references, lambda r: r.score).next()[1])

            # Calculate the winning stance. If there was a tie, we can only
            # determine the winner if all the references have the same stance.
            stance = self.UNCLEAR
            if len(set(r.stance for r in references)) == 1:
                stance = references[0].stance
        # No references.
        except StopIteration:
            stance = self.UNKNOWN

        if stance != self.stance:
            self.stance = stance
            self.save()

            # Save the issue to touch its updated_at timestamp. That way, when
            # a party's stance changes, the issue appears in the active steam.
            self.issue.save()
