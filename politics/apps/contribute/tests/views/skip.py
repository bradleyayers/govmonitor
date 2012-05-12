# coding=utf-8
from ...models import Task
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
from politics.utils.views import login_path


class SkipTestCase(TestCase):
    """Unit tests for the ``skip`` view."""

    fixtures = ("contribute_test_data", "core_test_data")

    def setUp(self):
        self.client = Client()
        self.client.login(username="chris", password="password")
        self.task_count = Task.objects.count()
        self.user = User.objects.get(pk=1)

    def test_skip(self):
        """The view should create a new task for the user, effectively skipping
            their previous task, and redirect to the contribution index."""
        original_task = Task.objects.get_for_user(self.user)
        response = self.client.post(reverse("contribute:skip"))

        self.assertRedirects(response, reverse("contribute:index"))
        self.assertEqual(self.task_count + 1, Task.objects.count())
        self.assertFalse(Task.objects.get(pk=original_task.pk).is_complete)

    def test_skip_not_authenticated(self):
        """The view should do nothing and redirect to the log in page if the
            client isn't authenticated."""
        self.client.logout()
        response = self.client.post(reverse("contribute:skip"))

        self.assertRedirects(response, login_path(reverse("contribute:index")))
        self.assertEqual(self.task_count, Task.objects.count())
