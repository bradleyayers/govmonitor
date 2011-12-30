# coding=utf-8
from django.contrib.contenttypes.models import ContentType
from django.db import models


class GenericManager(models.Manager):
    """A manager for models with generic foreign keys.

    Provides methods that are useful to such models: retrieve all instances
    linking to a particular model or linking to a particular model instance.

    Assumes that the ``ContentType`` foreign key field and the object ID field
    are named "content_type" and "object_id", respectively. If this isn't the
    case, subclass ``GenericManager`` and set the ``content_type_field_name``
    and ``object_id_field_name`` variables appropriately. For example:

    .. code-block:: python

        class ExampleManager(GenericManager):
            content_type_field_name = "subject_type"
            object_id_field_name = "subject_id"

            subject_type = models.ForeignKey("contenttypes.ContentType")
            subject_id = models.PositiveIntegerField()
    """

    content_type_field_name = "content_type"
    object_id_field_name = "object_id"

    # Use this manager everywhere.
    use_for_related_fields = True

    # We must extract this functionality into its own method, otherwise
    # overriding get_for_model() would always affect get_for_object().
    def _get_for_model(self, model):
        content_type = ContentType.objects.get_for_model(model)
        kwargs = {self.content_type_field_name: content_type}
        return self.get_query_set().filter(**kwargs)

    def get_for_model(self, model):
        """Returns instances that reference a particular model.

        :param model: The model in question.
        :type  model: ``django.db.models.ModelBase``
        :returns: Instances that reference instances of ``model``.
        :rtype: ``django.db.models.query.QuerySet``
        """
        return self._get_for_model(model)

    def get_for_object(self, object):
        """Returns instances that reference a particular model instance.

        :param object: The model instance in question.
        :type  object: ``django.db.models.Model``
        :returns: Instances that reference ``object``.
        :rtype: ``django.db.models.query.QuerySet``
        """
        # We can just pass object through to get_for_model because
        # ContentType's get_for_model accepts both models and instances.
        kwargs = {self.object_id_field_name: object.pk}
        return self._get_for_model(object).filter(**kwargs)
