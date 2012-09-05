# coding=utf-8
from autoslug.fields import AutoSlugField
from django.core.urlresolvers import reverse
from django.db import models


class Election(models.Model):
    """An election involving any number of parties.

    :ivar created_at: When the election was created.
    :type created_at: ``datetime.datetime``
    :ivar    held_on: When the election will be / was held.
    :type    held_on: ``datetime.datetime``
    :ivar     issues: The election's big issues.
    :type     issues: ``politics.apps.core.models.Issue``
    :ivar       name: The name of the election.
    :type       name: ``str``
    :ivar    parties: The parties involved in the election.
    :type    parties: ``politics.apps.core.models.Party``
    :ivar       slug: A slug version of the election's name.
    :type       slug: ``str``
    """

    created_at = models.DateTimeField(auto_now_add=True)
    held_on = models.DateField()
    issues = models.ManyToManyField("Issue")
    name = models.CharField(max_length=128)
    parties = models.ManyToManyField("Party")
    slug = AutoSlugField(always_update=True, max_length=128,
            populate_from="name")

    class Meta:
        app_label = "core"