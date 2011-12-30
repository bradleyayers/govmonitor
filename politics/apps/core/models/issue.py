# coding=utf-8
from autoslug.fields import AutoSlugField
from django.db import models
from politics.utils.models import MarkdownField


class Issue(models.Model):
    """An issue that a political party may have a view on.

    For example, the Australian Labor Party has a view on the carbon tax: they
    support it. The Liberal Party of Australia, on the other hand, opposes it.

    :ivar       created_at: When the issue was created.
    :type       created_at: ``datetime.datetime``
    :ivar      description: A description of the issue in Markdown format.
    :type      description: ``str``
    :ivar description_html: The issue's description converted to HTML.
    :type description_html: ``str``
    :ivar       is_popular: Whether the issue is "popular" and should thus be
                            shown on the home page.
    :type       is_popular: ``bool``
    :ivar             name: The name of the issue.
    :type             name: ``str``
    :ivar             tags: The tags assigned to this issue.
    :type             tags: :class:`Tag`
    :ivar       updated_at: When the issue was last updated.
    :type       updated_at: ``datetime.datetime``
    """

    created_at = models.DateTimeField(auto_now_add=True)
    description = MarkdownField(blank=True, disable=["images"], on_change=True)
    description_html = models.TextField(blank=True)
    is_popular = models.BooleanField(default=False)
    name = models.CharField(max_length=128)
    slug = AutoSlugField(always_update=True, max_length=128,
                         populate_from="name")
    tags = models.ManyToManyField("Tag")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "core"

    def __unicode__(self):
        return self.name

    @staticmethod
    def create_views(instance, created, **kwargs):
        """Creates initial views for a new issue.

        :param instance: The ``Issue`` that was saved.
        :type  instance: ``politics.apps.core.models.Issue``
        :param  created: Whether the ``Issue`` is newly created.
        :type   created: ``bool``
        """
        from politics.apps.core.models import Party, View

        if created:
            for party in Party.objects.all():
                View(issue=instance, party=party).save()

    def delete(self, *args, **kwargs):
        # Explicitly remove all tags to ensure that the many-to-many relation
        # change signal fires and the tags are removed if they become unused.
        self.tags.remove(*list(self.tags.all()))
        return super(Issue, self).delete(*args, **kwargs)

    @staticmethod
    def update_view_slugs(instance, **kwargs):
        """Update a issue's views' slugs.

        Called when an issue is saved to ensure that view slugs are correct
        (the issue's name might have been changed).

        :param instance: The :class:`Issue` that was saved.
        :type  instance: :class:`Issue`
        """
        for view in instance.view_set.all():
            view.save()


models.signals.post_save.connect(Issue.create_views, sender=Issue)
models.signals.post_save.connect(Issue.update_view_slugs, sender=Issue)
