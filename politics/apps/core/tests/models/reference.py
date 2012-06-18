# coding=utf-8
from django.contrib.auth.models import User
from django.core import mail
from django.test import TransactionTestCase
from politics.apps.comments.models import Comment
from politics.apps.core.models import Reference, View
from politics.apps.votes.models import Vote


class ReferenceTestCase(TransactionTestCase):
    """Unit tests for :class:`Reference`."""

    fixtures = ("core_test_data",)

    def test_author_vote(self):
        """When a reference is created, a :class:`Vote` should automatically be
            cast on it from its author, archiving their old vote."""
        user = User.objects.get(pk=1)
        view = View.objects.get(pk=1)
        vote_count = Vote.objects.count()
        reference = Reference.objects.get_or_create(author=user,
                stance=View.SUPPORT, text="", title="A Reference!",
                url="http://d.com/", view=view)[0]

        vote = Vote.objects.latest("pk")
        self.assertEqual(vote_count + 1, Vote.objects.count())
        self.assertEqual(vote.author, user)
        self.assertEqual(vote.content_object, reference)
        self.assertEqual(vote.type, Vote.UP)

    def test_comment_emails_author(self):
        """A reference's author should be emailed if someone comments on it."""
        reference = Reference.objects.get(pk=1)
        Comment(author=User.objects.get(pk=2), body="A comment!",
                content_object=reference).save()

        self.assertEqual(1, len(mail.outbox))
        self.assertEqual([reference.author.email], mail.outbox[0].to)

    def test_comment_emails_author_self(self):
        """A reference's author shouldn't be emailed if they comment on their
            own reference."""
        Comment(author=User.objects.get(pk=1), body="A comment!",
                content_object=Reference.objects.get(pk=1)).save()

        self.assertEqual(0, len(mail.outbox))

    def test_comment_emails_participants(self):
        """Participants in a reference's comment thread should be emailed if a
            new comment is posted."""
        Comment(author=User.objects.get(pk=1), body="A comment!",
                content_object=Reference.objects.get(pk=2)).save()

        self.assertEqual(2, len(mail.outbox))

        emails = {User.objects.get(pk=pk).email for pk in (2, 3)}
        self.assertEqual(emails, {email.to[0] for email in mail.outbox})
        self.assertTrue(all(len(email.to) == 1 for email in mail.outbox))

    def test_comment_emails_participants_self(self):
        """A participant in a reference's comment thread shouldn't be emailed
            when they post another comment in the same thread."""
        Comment(author=User.objects.get(pk=2), body="A comment!",
                content_object=Reference.objects.get(pk=2)).save()

        self.assertEqual(2, len(mail.outbox))

        emails = {User.objects.get(pk=pk).email for pk in (1, 3)}
        self.assertEqual(emails, {email.to[0] for email in mail.outbox})
        self.assertTrue(all(len(email.to) == 1 for email in mail.outbox))
