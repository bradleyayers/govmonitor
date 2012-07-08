# coding=utf-8
from django.contrib.auth.models import User
from django.db import models
import logging


class UserProfile(models.Model):
    """A user profile: used to store additional information about a user.

    As we can't modify ``django.contrib.auth.models.User``, we use the built-in
    "profile" mechanism to store additional information about users. Each user
    has an associated :class:`UserProfile` which can be accessed like so::

        user = User.objects.get(...)
        user_profile = user.get_profile()

    :ivar user: The user that the profile is associated with.
    :type user: ``django.contrib.auth.models.User``
    """

    user = models.OneToOneField(User)

    class Meta:
        app_label = "core"

    @staticmethod
    def create_user_profile(instance, created, **kwargs):
        """Creates a :class:`UserProfile` for a new ``User``.

        :param instance: The user that was created.
        :type  instance: ``django.contrib.auth.models.User``
        :param  created: Whether ``instance`` was just created.
        :type   created: ``bool``
        """
        if created:
            UserProfile(user=instance).save()
            logging.getLogger("email").info("New User", extra={"body":
                "%s registered on govmonitor." % instance.get_full_name()
            })


models.signals.post_save.connect(UserProfile.create_user_profile, sender=User)
