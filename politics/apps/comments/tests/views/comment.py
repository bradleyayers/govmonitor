# coding=utf-8
from datetime import datetime
from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client
import json
from politics.apps.comments.models import Comment
import reversion


class CommentViewTestCase(TestCase):
    """Unit tests for the ``comment`` view."""

    fixtures = ("comments_test_data", "core_test_data")

    def setUp(self):
        self.client = Client()
        self.client.login(username="chris", password="password")
        self.comment_count = Comment.objects.count()
        self.user = User.objects.get(pk=1)

    def test_delete(self):
        """It should be possible to delete a comment, providing that the client
            is authenticated and is the comment's author."""
        response = self.client.delete("/comments/1/")

        comment = Comment.objects.get(pk=1)
        self.assertEqual(200, response.status_code)
        self.assertTrue(comment.is_deleted)
        self.assertEqual(1, len(reversion.get_for_object(comment)))

    def test_delete_nonexistent(self):
        """Attempting to delete a comment that doesn't exist should fail,
            resulting in a 404 Not Found response."""
        response = self.client.delete("/comments/42/")

        self.assertEqual(404, response.status_code)

    def test_delete_not_authenticated(self):
        """Attempting to delete a comment when not authenticated should fail,
            resulting in a 401 Unauthorized response."""
        self.client.logout()
        response = self.client.delete("/comments/1/")

        comment = Comment.objects.get(pk=1)
        self.assertEqual(401, response.status_code)
        self.assertFalse(comment.is_deleted)
        self.assertEqual(0, len(reversion.get_for_object(comment)))

    def test_delete_not_author(self):
        """Attempting to delete a comment when the client is not the comment's
            author should fail, resulting in a 403 Forbidden response."""
        response = self.client.delete("/comments/2/")

        comment = Comment.objects.get(pk=2)
        self.assertEqual(403, response.status_code)
        self.assertFalse(comment.is_deleted)
        self.assertEqual(0, len(reversion.get_for_object(comment)))

    def test_edit(self):
        """It should be possible to edit a comment, providing that the client is
            authenticated and is the comment's author."""
        response = self.client.put("/comments/1/", {"body": "New body!"})

        comment = Comment.objects.get(pk=1)
        self.assertEqual(200, response.status_code)
        self.assertEqual(json.loads(response.content), comment.to_json())
        self.assertEqual("New body!", comment.body)
        self.assertEqual(1, len(reversion.get_for_object(comment)))

    def test_edit_deleted(self):
        """Attempting to edit a deleted comment should fail, resulting in a 400
            Bad Request response."""
        old_comment = Comment.objects.get(pk=3)
        response = self.client.put("/comments/3/", {"body": "New body!"})

        comment = Comment.objects.get(pk=3)
        self.assertEqual(400, response.status_code)
        self.assertEqual(old_comment.body, comment.body)
        self.assertEqual(0, len(reversion.get_for_object(comment)))

    def test_edit_invalid_fields(self):
        """Attempts to edit fields other than the body should fail silently."""
        old_comment = Comment.objects.get(pk=1)
        response = self.client.put("/comments/1/", {
            "author": 2,
            "body": "New body!",
            "created_at": datetime.now(),
            "content_type": 42,
            "is_deleted": True,
            "object_id": 42
        })

        comment = Comment.objects.get(pk=1)
        self.assertEqual(200, response.status_code)
        self.assertEqual(json.loads(response.content), comment.to_json())
        self.assertEqual(old_comment.author, comment.author)
        self.assertEqual("New body!", comment.body)
        self.assertEqual(old_comment.created_at, comment.created_at)
        self.assertEqual(old_comment.content_type, comment.content_type)
        self.assertEqual(old_comment.is_deleted, comment.is_deleted)
        self.assertEqual(old_comment.object_id, comment.object_id)
        self.assertEqual(1, len(reversion.get_for_object(comment)))

    def test_edit_invalid_values(self):
        """Providing invalid data when attempting to edit a comment should fail,
            resulting in a 400 Bad Request response."""
        old_comment = Comment.objects.get(pk=1)
        response = self.client.put("/comments/1/", {"body": ""})

        comment = Comment.objects.get(pk=1)
        self.assertEqual(400, response.status_code)
        self.assertEqual(old_comment.body, comment.body)
        self.assertEqual(0, len(reversion.get_for_object(comment)))

    def test_edit_nonexistent(self):
        """Attempting to edit a comment that doesn't exist should fail,
            resulting in a 404 Not Found response."""
        response = self.client.put("/comments/42/", {"body": "New body!"})

        self.assertEqual(404, response.status_code)

    def test_edit_not_author(self):
        """Attempting to edit a comment when the client is not the comment's
            author should fail, resulting in a 403 Forbidden response."""
        old_comment = Comment.objects.get(pk=2)
        response = self.client.put("/comments/2/", {"body": "New body!"})

        comment = Comment.objects.get(pk=2)
        self.assertEqual(403, response.status_code)
        self.assertEqual(old_comment.body, comment.body)
        self.assertEqual(0, len(reversion.get_for_object(comment)))

    def test_get(self):
        """Any GET request should fail, returning a 405 Method Not Allowed
            response."""
        response = self.client.get("/comments/1/")

        self.assertEqual(405, response.status_code)
