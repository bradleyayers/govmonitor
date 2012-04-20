# coding=utf-8
from django.contrib.contenttypes import generic
from django.db import models
from politics.apps.core.models.generic_manager import GenericManager


class Comment(models.Model):
    """A comment on an object.

    :ivar         author: The author of the comment.
    :type         author: ``django.contrib.auth.models.User``
    :ivar           body: The body of the comment.
    :type           body: ``str``
    :ivar     created_at: When the view occurred.
    :type     created_at: ``datetime.datetime``
    :ivar content_object: The object that was viewed.
    :type content_object: ``django.db.models.Model``
    :ivar   content_type: The type of the object that was viewed.
    :type   content_type: ``django.contrib.contenttypes.models.ContentType``
    :ivar      object_id: The ID of the object that was viewed.
    :type      object_id: ``int``
    """

    author = models.ForeignKey("auth.User")
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    content_object = generic.GenericForeignKey("content_type", "object_id")
    content_type = models.ForeignKey("contenttypes.ContentType")
    object_id = models.PositiveIntegerField()

    # Override the default manager.
    objects = GenericManager()

    def to_json(self):
        """Returns the comment as a dictionary, suitable to be encoded to JSON.

        :returns: A dictionary representation of the comment.
        :rtype: ``dict``
        """
        return {
            "author": {
                "first_name": self.author.first_name,
                "id": self.author.pk,
                "last_name": self.author.last_name,
            },
            "body": self.body,
            "created_at": str(self.created_at),
            "id": self.pk,
            "object_id": self.object_id,
        }
