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

    At the core of a ``View`` lies the party's ``stance`` on the issue: oppose,
    support, or unclear. This is calculated from :class:`Reference`s that have
    been submitted to the view, acting as evidence for one stance or another.

    Users vote on the submitted references, with the stance of the highest
    scoring reference used as the party's stance. Users may only vote on a
    single reference, but they may change their vote at any time. This ensures
    that new, high-quality references have the potential to rise to the top.
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

    # The party's apparent stance on the issue: the stance of the
    # :class:`Reference` with the greatest score. While this value could just
    # be calculated when required, we store it to make things nice and speedy.
    stance = models.CharField(choices=_STANCE_CHOICES, default=UNKNOWN,
                              max_length=7)

    class Meta:
        app_label = "core"

    def __unicode__(self):
        return "%s, %s" % (self.party.name, self.issue.name)

    def get_vote_for_user(self, user):
        """Retrieve a user's vote within the view.

        :param user: The user.
        :type  user: ``django.contrib.auth.models.User``
        :returns: ``user``'s vote or ``None`` if they haven't voted.
        :rtype: :class:`ReferenceVote` or ``None``

        .. note::

            Assumes that the user cannot cast more than one vote; if they have
            somehow cast multiple, then the system is in an inconsistent state.
        """
        from . import ReferenceVote

        try:
            votes = ReferenceVote.objects.get_for_view(self)
            return votes.filter(author=user)[0]
        except IndexError:
            return None

    def withdraw_vote(self, user):
        """Withdraw a user's vote within the view.

        :param user: The user.
        :type  user: ``django.contrib.auth.models.User``
        """
        vote = self.get_vote_for_user(user)

        if vote:
            vote.is_archived = True
            vote.save()

    def cast_vote(self, reference, user):
        """Cast a vote on one of the view's references.

        The user's existing vote (if any) is withdrawn.

        :param reference: The reference to vote for.
        :type  reference: ``politics.apps.core.models.Reference``
        :param      user: The user casting the vote.
        :type       user: ``django.contrib.auth.models.User``
        """
        from . import ReferenceVote

        self.withdraw_vote(user)
        ReferenceVote(content_object=reference, author=user).save()

    def refresh_stance(self):
        """Recalculate the view's ``stance``.

        A view's stance is equal to that of the :class:`Reference` with the
        greatest number of non-archived votes (the "best" reference).

        This method assumes that the view's :class:`Reference`s are up to date
        (their scores reflect the votes cast). If the stance changes, the
        :class:`Issue` is saved to touch its ``updated_at`` timestamp.
        """
        from politics.apps.core.models import Issue
        from politics.apps.core.tasks import calculate_party_similarities

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
            # a party's stance changes, the issue appears in the active stream.
            # In cascading deletes, the issue may not exist anymore.
            try:
                self.issue.save()
            except Issue.DoesNotExist:
                pass

            calculate_party_similarities.delay(self.party.pk)
