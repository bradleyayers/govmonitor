# coding=utf-8
from ...models import Task
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.test import TransactionTestCase
from django.test.client import Client
from politics.apps.core.models import Reference, View
from politics.utils.views import login_path


class IndexTestCase(TransactionTestCase):
    """Unit tests for the ``index`` view."""

    fixtures = ("contribute_test_data", "core_test_data")

    def setUp(self):
        self.client = Client()
        self.client.login(username="chris", password="password")
        self.task_count = Task.objects.count()
        self.user = User.objects.get(pk=1)

    def test_index_existing_task(self):
        """If the user has already been assigned a task view should show it."""
        self.client.get(reverse("contribute:index"))
        self.assertEqual(self.task_count, Task.objects.count())

    def test_index_no_task(self):
        """If the user is yet to be assigned a task, view should select one for
            them and record the selection by creating a :class:`Task` object."""
        self.client = Client()
        self.client.login(username="brad", password="password")
        self.user = User.objects.get(pk=2)
        self.client.get(reverse("contribute:index"))

        self.assertEqual(self.task_count + 1, Task.objects.count())
        self.assertEqual(self.user, Task.objects.latest("pk").user)

    def test_index_not_authenticated(self):
        """The view should do nothing and redirect to the log in page if the
            client isn't authenticated."""
        self.client.logout()
        response = self.client.get(reverse("contribute:index"))

        self.assertRedirects(response, login_path(reverse("contribute:index")))
        self.assertEqual(self.task_count, Task.objects.count())

    def test_index_submit_reference(self):
        """If the user POSTs reference data, the view should create a reference
            for the view associated with the user's current task, and create a
            new task for the user."""
        reference_count = Reference.objects.count()
        self.client.post(reverse("contribute:index"), {
            "stance": View.SUPPORT,
            "text": "This is a new reference!",
            "title": "Reference",
            "url": "http://www.atlassian.com/",
        })

        original_task = Task.objects.get(pk=1)
        self.assertTrue(original_task.is_complete)
        self.assertEqual(self.task_count + 1, Task.objects.count())
        self.assertEqual(reference_count + 1, Reference.objects.count())
        self.assertNotEqual(original_task, Task.objects.get_for_user(self.user))

        reference = Reference.objects.latest("pk")
        self.assertEqual(self.user, reference.author)
        self.assertEqual(View.SUPPORT, reference.stance)
        self.assertEqual(original_task.view, reference.view)
        self.assertEqual("This is a new reference!", reference.text)
        self.assertEqual("http://www.atlassian.com/", reference.url)
