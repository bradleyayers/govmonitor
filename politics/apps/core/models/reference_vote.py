# coding=utf-8
from . import Reference, Vote, VotesManager
from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError, models


class ReferenceVotesManager(VotesManager):
    """The default :class:`ReferenceVote` manager."""

    def get_for_view(self, view, include_archived=False):
        """Returns votes that have been cast on a particular view's references.

        :param             view: The view in question.
        :type              view: :class:`View`
        :param include_archived: Whether archived votes should be included.
        :type  include_archived: ``bool``
        :returns: :class:`ReferenceVote`s that have been cast on
                  :class:`Reference`s within ``view``.
        :rtype: ``django.db.models.query.QuerySet`` of :class:`ReferenceVote`s
        """
        if include_archived:
            query_set = self.get_query_set()
        else:
            query_set = self.not_archived()

        reference_pks = [r.pk for r in view.reference_set.all()]
        return query_set.filter(object_id__in=reference_pks)

    def get_query_set(self):
        # Only return votes on References. We can't call get_for_model()
        # because that calls get_query_set(), leading to a stack overflow.
        content_type = ContentType.objects.get_for_model(Reference)
        query_set = super(ReferenceVotesManager, self).get_query_set()
        return query_set.filter(content_type=content_type)


class ReferenceVote(Vote):
    """A vote on a :class:`Reference`.

    A user may only vote on one :class:`Reference` within a :class:`View`: in
    the set of non-archived :class:`ReferenceVote`s, the ``content_object``,
    ``author`` pair must be unique. Votes can be archived to allow new ones.
    """

    # Override the default manager.
    objects = ReferenceVotesManager()

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        """Save the instance to the database.

        :raises IntegrityError: If ``content_object`` isn't a :class:`Reference`.
        :raises IntegrityError: If ``author`` has already voted on a reference
                                within the view (and it's not archived).
        """
        if not isinstance(self.content_object, Reference):
            raise IntegrityError("content_object must be a Reference.")

        # Has the user already voted in the view (exluding this vote)?
        votes = ReferenceVote.objects.get_for_view(self.content_object.view)
        votes = votes.filter(author=self.author).exclude(pk=self.pk)

        if votes.exists():
            raise IntegrityError("Duplicate vote.")

        super(ReferenceVote, self).save(*args, **kwargs)


# We must hook refresh_score() up; otherwise it would only be called on Votes.
# ReferenceVotes won't typically be deleted, but hook up post_delete anyway.
models.signals.post_delete.connect(Vote.refresh_score, sender=ReferenceVote)
models.signals.post_save.connect(Vote.refresh_score, sender=ReferenceVote)
