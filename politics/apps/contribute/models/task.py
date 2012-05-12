# coding=utf-8
from django.db import models


class TaskManager(models.Manager):
    """The contribution task manager."""

    # Use this manager everywhere.
    use_for_related_fields = True

    def get_for_user(self, user):
        """Retrieve the given user's current contribution task, if any.

        :param user: The user whos contribution task is to be retrieved.
        :type  user: ``django.contrib.auth.models.User``
        :returns: ``user``'s current contribution task if it exists.
        :rtype: ``politics.apps.contribute.models.Task`` or ``None``
        """
        tasks = self.get_query_set().filter(user=user).order_by("-pk")
        return tasks[0] if len(tasks) > 0 and not tasks[0].is_complete else None


class Task(models.Model):
    """A contribution task that has been requested of a user.

    When a user navigates to the "contribute" page, they are assigned a task to
    complete (e.g. find a reference for a view). This model is used to record
    the task that was assigned so they can return to it later.

    :ivar        user: The user the task was assigned to.
    :type        user: ``django.contrib.auth.models.User``
    :ivar        view: The view associated with the task.
    :type        view: ``politics.apps.core.models.View``
    :ivar is_complete: Whether the task is complete.
    :type is_complete: ``boolean``
    """

    user = models.ForeignKey("auth.User")
    view = models.ForeignKey("core.View")
    is_complete = models.BooleanField(default=False)

    # Override the default manager.
    objects = TaskManager()

    class Meta:
        app_label = "contribute"
