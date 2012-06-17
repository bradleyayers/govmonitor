# coding=utf-8
from ..models import Task
from django.contrib.auth.models import User
from django.test import TransactionTestCase
from politics.apps.core.models import View


class TaskTestCase(TransactionTestCase):
    """Unit tests for the ``Task`` model."""

    fixtures = ("contribute_test_data", "core_test_data")

    def test_get_for_user(self):
        """The manager's ``get_for_user`` method should return the given user's
            current task."""
        task = Task.objects.get_for_user(User.objects.get(pk=1))
        self.assertEqual(Task.objects.get(pk=1), task)

    def test_get_for_user_complete(self):
        """The manager's ``get_for_user`` method should return ``None`` if the
            user's last task is complete and they haven't got a new one."""
        user = User.objects.get(pk=1)
        Task(is_complete=True, user=user, view=View.objects.get(pk=1)).save()
        self.assertIsNone(Task.objects.get_for_user(user))

    def test_get_for_user_none(self):
        """The manager's ``get_for_user`` method should return ``None`` if the
            user doesn't currently have a task."""
        self.assertIsNone(Task.objects.get_for_user(User.objects.get(pk=2)))
