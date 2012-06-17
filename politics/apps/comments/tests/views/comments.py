# coding=utf-8
from django.contrib.auth.models import AnonymousUser, User
from django.contrib.contenttypes.models import ContentType
from django.test import TransactionTestCase
import fudge
import json
from politics.apps.comments.models import Comment
from politics.apps.comments.views import comments
import reversion


class CommentsViewTestCase(TransactionTestCase):
    """Unit tests for the generic ``comments`` view."""

    fixtures = ("core_test_data",)

    def setUp(self):
        self.comment_count = Comment.objects.count()
        self.user = User.objects.get(pk=1)

    def test_create(self):
        """Attempting to create a comment when authenticated and with valid data
            should succeed, resulting in a 201 Created response."""
        request = fudge.Fake("HttpRequest").has_attr(
            method="POST",
            POST={"body": "A comment!"},
            user=self.user
        )

        response = comments(request, self.user)
        self.assertEqual(201, response.status_code)
        self.assertEqual(self.comment_count + 1, Comment.objects.count())

        # Was the comment created correctly?
        comment = Comment.objects.latest("pk")
        self.assertEqual(self.user, comment.author)
        self.assertEqual("A comment!", comment.body)
        self.assertEqual(self.user, comment.content_object)
        self.assertFalse(comment.is_deleted)

        # Was an initial version of the comment created?
        self.assertEqual(1, len(reversion.get_for_object(comment)))

        # Was the response the comment as JSON?
        self.assertEqual(json.loads(response.content), comment.to_json())

    def test_create_invalid(self):
        """Attempting to create a comment with invalid data should fail,
            resulting in a 400 Bad Request response."""
        request = fudge.Fake("HttpRequest").has_attr(
            method="POST",
            POST={"body": ""},
            user=self.user
        )

        response = comments(request, self.user)
        self.assertEqual(400, response.status_code)
        self.assertEqual(self.comment_count, Comment.objects.count())

    def test_create_not_authenticated(self):
        """Attempting to create a comment when not authenticated should fail,
            resulting in a 401 Unauthorized response."""
        request = fudge.Fake("HttpRequest").has_attr(
            method="POST",
            user=AnonymousUser()
        )

        response = comments(request, None)
        self.assertEqual(401, response.status_code)
        self.assertEqual(self.comment_count, Comment.objects.count())

    def test_create_security(self):
        """The client must not be able to set the comment's ``content_object``
            by providing ``content_type`` or ``object_id``."""
        request = fudge.Fake("HttpRequest").has_attr(
            method="POST",
            POST={
                "content_type": ContentType.objects.get_for_model(User).pk,
                "body": "A comment!",
                "object_id": 2,
            },
            user=self.user
        )

        response = comments(request, self.user)
        self.assertEqual(201, response.status_code)
        self.assertEqual(self.comment_count + 1, Comment.objects.count())
        self.assertEqual(self.user, Comment.objects.latest("pk").content_object)
