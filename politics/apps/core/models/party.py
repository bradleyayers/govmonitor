# coding=utf-8
from autoslug.fields import AutoSlugField
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey


class Party(MPTTModel):
    """A political party.

    :ivar created_at: When the party model was created.
    :type created_at: ``datetime.datetime``
    :ivar       name: The name of the party.
    :type       name: ``str``
    :ivar     parent: The parent party of which this is a subsidiary.
    :type     parent: :class:`Party`
    :ivar    picture: The party's picture.
    :type    picture: ``django.db.models.FileField``
    :ivar       slug: A slug version of the party's name.
    :type       slug: ``str``
    """

    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=64)
    parent = TreeForeignKey("self", blank=True, null=True,
            related_name="children")
    picture = models.ImageField(blank=True, null=True,
            upload_to="party_pictures")
    slug = AutoSlugField(always_update=True, max_length=64,
            populate_from="name")

    class Meta:
        app_label = "core"
        verbose_name_plural = "parties"

    class MPTTMeta:
        left_attr = "tree_left"
        level_attr = "tree_level"
        right_attr = "tree_right"

    def __unicode__(self):
        return self.name

    def get_picture(self):
        """
        :returns: The party's picture or the default if it doesn't have one.
        :rtype: ``django.db.models.fields.files.FieldFile`` or ``str``
        """
        return self.picture if self.picture else "party_pictures/default.png"

    @staticmethod
    def update_view_slugs(instance, **kwargs):
        """Update a party's views' slugs.

        Called when a party is saved to ensure that view slugs are correct
        (the party's name might have been changed).
        """
        for view in instance.view_set.all():
            view.save(touch_updated_at=False)

    @property
    def percentage_views_known(self):
        """Calculates the percentage of the party's views that are known.

        :returns: The percentage of the party's views that are known.
        :rtype: ``float``
        """
        from . import Issue, View

        issues = Issue.objects.all()
        known_views = self.view_set.exclude(stance=View.UNKNOWN)

        return known_views.count() * 100.0 / max(1, issues.count())


models.signals.post_save.connect(Party.update_view_slugs, sender=Party)