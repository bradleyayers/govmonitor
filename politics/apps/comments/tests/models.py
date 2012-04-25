# coding=utf-8
from django.contrib.auth.models import User
from django.test import TestCase
from politics.apps.comments.models import Comment


class CommentTestCase(TestCase):
    """Unit tests for the ``Comment`` model."""

    fixtures = ("comments_test_data", "core_test_data")

    def test_get_earlier_authors(self):
        """``get_earlier_authors`` should return the set of users who
            participated in the thread before the comment was posted."""
        comment = Comment.objects.get(pk=3)
        authors = {User.objects.get(pk=pk) for pk in (1, 2)}
        self.assertEqual(authors, comment.get_earlier_authors())

    def test_get_earlier_authors_first(self):
        """``get_earlier_authors`` should return an empty set if the comment is
            the first comment in a thread."""
        comment = Comment.objects.get(pk=1)
        self.assertEqual(set(), comment.get_earlier_authors())

    def test_get_earlier_authors_same_author(self):
        """The set returned from ``get_earlier_authors`` should include the
            comment's author, if appropriate."""
        comment = Comment.objects.get(pk=4)
        authors = {User.objects.get(pk=pk) for pk in (1, 2, 3)}
        self.assertEqual(authors, comment.get_earlier_authors())
