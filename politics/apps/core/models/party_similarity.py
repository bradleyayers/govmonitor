# coding=utf-8
from django.db import models
from politics.apps.core.models import ArchiveManager


class PartySimilarity(models.Model):
    """A record of the similarity between two parties at a point in time.

    The similarity between two parties is a measure of how many views they
    share: if their views differ on all issues, their similarity is 0; if
    they're all the same, it is 100. It will likely fall somewhere in-between.

    As :class:`PartySimilarity` objects aren't deleted, the most recently
    created object referencing two parties is to be considered "correct".

    :ivar   created_at: When the object was created.
    :type   created_at: ``datetime.datetime``
    :ivar  first_party: The first party.
    :type  first_party: :class:`Party`
    :ivar  is_archived: Whether the object is archived.
    :type  is_archived: ``bool``
    :ivar second_party: The second party.
    :type second_party: :class:`Party`
    :ivar   similarity: The similarity between the parties.
    :type   similarity: ``float``
    """

    created_at = models.DateTimeField(auto_now_add=True)
    first_party = models.ForeignKey("Party")
    is_archived = models.BooleanField(default=False)
    second_party = models.ForeignKey("Party", related_name="+")
    similarity = models.FloatField()

    # Override the default manager.
    objects = ArchiveManager()

    class Meta:
        app_label = "core"

    def percentage_similarity(self):
        """Returns ``similarity`` as a percentage."""
        return self.similarity * 100

    def save(self, *args, **kwargs):
        # Validate the similarity value.
        if not 0 <= self.similarity <= 100:
            raise ValueError("similarity must be between 0 and 100 inclusive.")

        super(PartySimilarity, self).save(*args, **kwargs)
