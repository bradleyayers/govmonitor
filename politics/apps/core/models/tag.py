# coding=utf-8
from . import Issue
from autoslug.fields import AutoSlugField
from django.db import models
from django.db.models import Count
import reversion


class Tag(models.Model):
    """A marker to group logically related issues.

    :ivar  created_at: When the tag was created.
    :type  created_at: ``datetime.datetime``
    :ivar        name: The name of the tag.
    :type        name: ``str``
    :ivar        slug: A slug version of the tag's name.
    :type        slug: ``str``
    """

    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=32, unique=True)
    slug = AutoSlugField(always_update=True, max_length=64,
                         populate_from="name")

    class Meta:
        app_label = "core"

    def __unicode__(self):
        return self.name

    @staticmethod
    def delete_unused(action, instance, pk_set, **kwargs):
        """Deletes :class:`Tag`s that are no longer being used.

        Called when a change is made to the issue, tag many-to-many
        relationship. We only consider objects involved in the change.

        :class:`Issue`'s ``delete()`` explicitly removes all tags to ensure
        that this is called for each of the issue's tags before it is deleted.

        :param   action: The type of change that was / will be made.
        :type    action: ``str``
        :param instance: The object whose relationship was / will be modified.
        :type  instance: :class:`Issue` or :class:`Tag`
        :param   pk_set: The IDs of objects added or removed from the relation.
        :type    pk_set: ``set``
        """
        # We only care about removals.
        if action != "post_remove":
            return

        if isinstance(instance, Tag):
            pk_set = [instance.pk]

        # Delete all tags that are now unused.
        tags = Tag.objects.filter(pk__in=pk_set).annotate(Count("issue"))
        [tag.delete() for tag in tags if tag.issue__count == 0]


models.signals.m2m_changed.connect(Tag.delete_unused,
                                   sender=Issue.tags.through)


# While changes to tags aren't versioned, we must register the model with
# django-reversion so an issue's tags can be stored when it is versioned.
reversion.register(Tag)
