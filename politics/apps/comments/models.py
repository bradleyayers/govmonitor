# coding=utf-8
from django.contrib.contenttypes import generic
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from politics.apps.core.models.generic_manager import GenericManager


class Comment(models.Model):
    """A comment on an object.

    Models can be notified when comments are made on them by implementing a
    method ``handle_comment_created`` that takes the new comment as an argument.

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
    :ivar     is_deleted: Whether the comment has been deleted.
    :type     is_deleted: ``bool``
    :ivar      object_id: The ID of the object that was viewed.
    :type      object_id: ``int``
    """

    author = models.ForeignKey("auth.User")
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    content_object = generic.GenericForeignKey("content_type", "object_id")
    content_type = models.ForeignKey("contenttypes.ContentType")
    is_deleted = models.BooleanField(default=False)
    object_id = models.PositiveIntegerField()

    # Override the default manager.
    objects = GenericManager()

    def get_absolute_url(self):
        """Returns the comment's absolute URL.

        This is based on the value returned from the content object's
        ``get_comment_thread_url`` (a hash is appended to identify the comment).
        """
        comments_url = self.content_object.get_comment_thread_url()
        return "%s#comment-%d" % (comments_url, self.pk)

    def get_earlier_authors(self):
        """Returns the users who participated in the thread before this comment.

        :returns: The set of users who participated in the thread before this
                  comment (potentially including the author of this comment).
        :rtype: ``set`` of ``django.contrib.auth.models.User``
        """
        earlier_comments = Comment.objects.get_for_instance(self.content_object)
        earlier_comments = earlier_comments.filter(pk__lt=self.pk)
        return {comment.author for comment in earlier_comments}

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
            "is_deleted": self.is_deleted,
            "object_id": self.object_id,
        }


@receiver(post_save, sender=Comment)
def _notify_object_of_comment_creation(instance, created, **kwargs):
    """Notify an object that a comment has been made on it.

    :param  created: Whether the comment is new.
    :type   created: ``bool``
    :param instance: The comment that was created.
    :type  instance: ``politics.apps.comments.models.Comment``
    """
    try:
        if created and not kwargs.get("raw"):
            instance.content_object.handle_comment_created(instance)
    except AttributeError:
        pass
