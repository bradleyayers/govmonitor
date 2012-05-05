# coding=utf-8
from django.contrib.contenttypes import generic
from django.db import models
from politics.apps.core.models.generic_manager import GenericManager


class View(models.Model):
    """A record of a user viewing an object.

    :ivar     created_at: When the view occurred.
    :type     created_at: ``datetime.datetime``
    :ivar content_object: The object that was viewed.
    :type content_object: ``django.db.models.Model``
    :ivar   content_type: The type of the object that was viewed.
    :type   content_type: ``django.contrib.contenttypes.models.ContentType``
    :ivar     ip_address: The IP address of the user doing the viewing.
    :type     ip_address: ``str``
    :ivar      object_id: The ID of the object that was viewed.
    :type      object_id: ``int``
    """

    created_at = models.DateTimeField(auto_now_add=True)
    content_object = generic.GenericForeignKey("content_type", "object_id")
    content_type = models.ForeignKey("contenttypes.ContentType")
    ip_address = models.IPAddressField()
    object_id = models.PositiveIntegerField()

    # Override the default manger.
    objects = GenericManager()
