# coding=utf-8
from .fields import ScoreField
from django.contrib.contenttypes import generic
from django.db import IntegrityError, models
from django.db.models import Count
from politics.apps.core.models.generic_manager import GenericManager
from math import sqrt


class VotesManager(GenericManager):
    """The default :class:`Vote`s manager.

    ``get_for_model()`` and ``get_for_instance()`` both take an additional
    argument ``include_archived``. If it is ``True``, the result will include
    archived votes, if ``False`` (the default), they will be filtered out.
    """

    def get_for_model(self, model, include_archived=False):
        votes = super(VotesManager, self).get_for_model(model)
        return votes if include_archived else votes.filter(is_archived=False)

    def get_for_instance(self, instance, include_archived=False):
        votes = super(VotesManager, self).get_for_instance(instance)
        return votes if include_archived else votes.filter(is_archived=False)

    def not_archived(self):
        """Returns votes that aren't archived.

        :returns: :class:`Vote`s where ``is_archived`` is ``False``.
        :rtype: ``django.db.models.query.QuerySet`` of :class:`View`s
        """
        return self.get_query_set().filter(is_archived=False)


class Vote(models.Model):
    """A user's vote on a model.

    A generic foreign key is used to reference the subject of the vote:

    .. code-block:: python

        vote = Vote(author=..., content_object=MyModel.objects.get(...))

    A ``GenericRelation`` must be added to models that will be voted on to
    ensure that deletes cascade to votes. A useful side effect: this provides
    quick access to all votes that have been cast on a model.

    .. code-block:: python

        from django.contrib.contenttypes import generic
        from django.db import models


        class MyModel(models.Model):
            votes = generic.GenericRelation("votes.Vote")

    The default manager ``objects`` provides a number of shortcut methods. See
    the :class:`VotesManager` documentation for more information.

    :ivar         author: The user that cast the vote.
    :type         author: ``django.contrib.auth.models.User``
    :ivar content_object: The subject of vote.
    :type content_object: ``django.db.models.Model``
    :ivar   content_type: The type of the subject of the vote.
    :type   content_type: ``django.contrib.contenttypes.models.ContentType``
    :ivar     created_at: When the vote was cast.
    :type     created_at: ``datetime.datetime``
    :ivar    is_archived: Whether the vote has been archived.
    :type    is_archived: ``bool``
    :ivar      object_id: The ID of the subject of the vote.
    :type      object_id: ``int``
    :ivar           type: The vote's type (up or down).
    :type           type: ``str``
    """

    # Types
    UP = "up"
    DOWN = "down"
    TYPE_CHOICES = ((UP, "Up"), (DOWN, "Down"))

    author = models.ForeignKey("auth.User")
    content_object = generic.GenericForeignKey("content_type", "object_id")
    content_type = models.ForeignKey("contenttypes.ContentType")
    created_at = models.DateTimeField(auto_now_add=True)
    is_archived = models.BooleanField(default=False)
    object_id = models.PositiveIntegerField()
    type = models.CharField(choices=TYPE_CHOICES, max_length=4)

    # Override the default manager.
    objects = VotesManager()

    class Meta:
        app_label = "votes"

    @staticmethod
    def refresh_score(instance, **kwargs):
        """Update the subject's score if it has a :class:`ScoreField`.

        :param instance: The :class:`Vote` that was deleted or saved.
        :type  instance: :class:`Vote`
        """
        # Returns the lower bound of a sample's Wilson score interval with 95%
        # confidence. n is the sample size, p is the observed proportion.
        def _wilson(n, p):
            z = 1.65 # 95%
            z2 = z * z
            result = p + z2 / (2 * n)
            result = result - z * sqrt((p * (1 - p)) / n + z2 / (4 * n * n))
            return result / (1 + z2 / n)

        # The subject will be None in cascading deletes.
        subject = instance.content_object
        if subject is None:
            return

        # The votes are passed in when we're running in a migration.
        votes = kwargs.pop("votes", Vote.objects.get_for_instance(subject))
        votes = votes.values("type").annotate(count=Count("type"))
        votes = dict((v["type"], 1.0 * v["count"]) for v in votes)

        up = votes.get(Vote.UP, 0.0)
        total = up + votes.get(Vote.DOWN, 0.0)
        score = _wilson(total, up / total) if total > 0 else 0

        # Update all the subject's ScoreFields.
        for field in subject._meta.fields:
            if isinstance(field, ScoreField):
                setattr(subject, field.name, score)

        subject.save()

    def save(self, *args, **kwargs):
        # Ensure that the user hasn't already voted on this object. It's the
        # caller's responsibility to archive votes before creating new ones.
        votes = Vote.objects.get_for_instance(self.content_object)
        votes = votes.filter(author=self.author).exclude(pk=self.pk)

        if votes.exists():
            raise IntegrityError("Duplicate vote.")

        super(Vote, self).save(*args, **kwargs)



# The post_delete signal won't fire often (if at all) because votes should be
# archived, not deleted. Hook it up to make sure that state stays consistent.
models.signals.post_delete.connect(Vote.refresh_score, sender=Vote)
models.signals.post_save.connect(Vote.refresh_score, sender=Vote)
