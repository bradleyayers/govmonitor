# coding=utf-8
from autoslug.fields import AutoSlugField
from django.db import models
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


# While changes to tags aren't versioned, we must register the model with
# django-reversion so an issue's tags can be stored when it is versioned.
reversion.register(Tag)
