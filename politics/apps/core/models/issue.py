# coding=utf-8
from autoslug.fields import AutoSlugField
from django.db import models
from politics.utils.models import MarkdownField
import reversion


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
    :ivar             name: The name of the issue.
    :type             name: ``str``
    :ivar             slug: A slug version of the issue's name.
    :type             slug: ``str``
    :ivar             tags: The tags assigned to this issue.
    :type             tags: :class:`Tag`
    :ivar       updated_at: When the issue was last updated.
    :type       updated_at: ``datetime.datetime``
    """

    created_at = models.DateTimeField(auto_now_add=True)
    description = MarkdownField(blank=True, disable=["images"], on_change=True)
    description_html = models.TextField(blank=True)
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
    def common_tags(issues):
        """Extract tags from a set of issues, ordering them by frequency.

        :param issues: The issues from which tags will be extracted.
        :type  issues: *iterable* of :class:`Issue`s
        :returns: A list of unique tags referenced by elements of ``issues``,
                  in descending order of how many times they were referenced.
        :rtype: ``list`` of :class:`Tag`s
        """
        tags = sum((list(issue.tags.all()) for issue in issues), [])
        return sorted(set(tags), key=tags.count, reverse=True)

    def delete(self, *args, **kwargs):
        # Explicitly remove all tags to ensure that the many-to-many relation
        # change signal fires and the tags are removed if they become unused.
        self.tags.remove(*list(self.tags.all()))
        return super(Issue, self).delete(*args, **kwargs)

    @property
    def percentage_views_known(self):
        """Returns the percentage of views that are known for this issue."""
        from . import Party, View

        root_parties = Party.objects.filter(tree_level=0)
        known_views = (self.view_set.filter(party__in=root_parties)
                .exclude(stance=View.UNKNOWN))

        return known_views.count() * 100.0 / max(1, root_parties.count())


# As tags are deleted when they become unused, we must store them alongside
# issues; otherwise, the tags might not be available when we revert an issue.
reversion.register(Issue, follow=["tags"])