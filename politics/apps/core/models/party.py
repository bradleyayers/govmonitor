# coding=utf-8
from autoslug.fields import AutoSlugField
from django.db import models


class Party(models.Model):
    """A political party.

    :ivar created_at: When the party model was created.
    :type created_at: ``datetime.datetime``
    :ivar       name: The name of the party.
    :type       name: ``str``
    :ivar       slug: A slug version of the party's name.
    :type       slug: ``str``
    """

    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=64)
    slug = AutoSlugField(always_update=True, max_length=64,
                         populate_from="name")

    class Meta:
        app_label = "core"
        verbose_name_plural = "parties"

    def __unicode__(self):
        return self.name

    @staticmethod
    def create_views(instance, created, **kwargs):
        """Creates initial views for a new ``Party``.

        :param instance: The ``Party`` that was saved.
        :type  instance: ``politics.apps.core.models.Party``
        :param  created: Whether the ``Party`` is newly created.
        :type   created: ``bool``
        """
        from politics.apps.core.models import Issue, View

        if created:
            for issue in Issue.objects.all():
                View(issue=issue, party=instance).save()

    @staticmethod
    def update_view_slugs(instance, **kwargs):
        """Update a party's views' slugs.

        Called when a party is saved to ensure that view slugs are correct
        (the party's name might have been changed).
        """
        for view in instance.view_set.all():
            view.save()


models.signals.post_save.connect(Party.create_views, sender=Party)
models.signals.post_save.connect(Party.update_view_slugs, sender=Party)
