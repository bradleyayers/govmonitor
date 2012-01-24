# coding=utf-8
from django.db import models


class ArchiveManager(models.Manager):
    """A manager with support for "archivable" models."""

    # Use this manager everywhere.
    use_for_related_fields = True

    def __init__(self, *args, **kwargs):
        """Initialise the manager.

        :param field_name: The name of the "is_archived" field.
        :type  field_name: ``str``
        """
        super(ArchiveManager, self).__init__(*args, **kwargs)
        self._field_name = kwargs.pop("field_name", "is_archived")

    def not_archived(self):
        """Returns objects that aren't archived.

        :returns: Objects that aren't archived.
        """
        return self.get_query_set().filter(**{self._field_name: False})
