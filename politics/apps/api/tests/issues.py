# coding=utf-8
from django.core.urlresolvers import reverse
from django.test import TransactionTestCase
from django.test.client import Client
import json
from politics.apps.core.models import Issue, Party, View


class IssueViewsTestCase(TransactionTestCase):
    """Unit tests for the API's issue views."""

    fixtures = ("core_test_data",)

    def setUp(self):
        self.client = Client()

    def test_show(self):
        """The ``show`` view should return information about an issue."""
        issue = Issue.objects.get(pk=1)
        response = self.client.get(reverse("api:issues:show",
                kwargs={"pk": issue.pk}))

        data = json.loads(response.content)
        views = issue.view_set.exclude(stance=View.UNKNOWN)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(data["name"], issue.name)
        self.assertEquals(len(data["views"]), len(views))

        name = "Australian Labor Party"
        view = next(v for v in data["views"] if v["party"]["name"] == name)
        self.assertEqual(view, {
            "party": {"name": name},
            "stance": "support",
            "url": "http://govmonitor.org/issues/1-carbon-tax/parties/1-australian-labor-party/"
        })

    def test_show_invalid_names(self):
        """The ``show`` view should escape names to ensure valid JSON."""
        Issue.objects.filter(pk=4).update(name="\"")
        Party.objects.filter(pk=1).update(name="\"")
        response = self.client.get(reverse("api:issues:show",
                kwargs={"pk": 4}))

        self.assertEqual(response.status_code, 200)

        # Only party 1 has a view.
        data = json.loads(response.content)
        self.assertEqual(data["name"], "\"")
        self.assertEqual(data["views"][0]["party"]["name"], "\"")

    def test_show_jsonp(self):
        """The ``show`` view should support JSONP via a callback parameter."""
        path = reverse("api:issues:show", kwargs={"pk": 1})
        data = self.client.get(path).content
        response = self.client.get(path + "?callback=foo")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, "foo(%s)" % data)

    def test_show_nonexistent(self):
        """The ``show`` view should return 404 Not Found if there's no issue in
            the database with the given pk."""
        response = self.client.get(reverse("api:issues:show",
                kwargs={"pk": 1337}))

        self.assertEqual(response.content, "")
        self.assertEqual(response.status_code, 404)
