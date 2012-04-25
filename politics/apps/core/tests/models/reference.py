# coding=utf-8
from django.contrib.auth.models import User
from django.core import mail
from django.test import TransactionTestCase
from politics.apps.comments.models import Comment
from politics.apps.core.models import Reference, ReferenceVote, View


class ReferenceTestCase(TransactionTestCase):
    """Unit tests for :class:`Reference`."""

    fixtures = ("core_test_data",)

    def test_author_vote(self):
        """When a reference is created, a :class:`Vote` should automatically be
            cast on it from its author, archiving their old vote."""
        user = User.objects.get(pk=1)
        view = View.objects.get(pk=1)
        vote = view.get_vote_for_user(user)

        # A vote should automatically be cast for this.
        reference = Reference(author=user, stance=View.SUPPORT, text="",
                              url="http://d.com/", view=view)
        reference.save()

        new_vote = view.get_vote_for_user(user)
        self.assertNotEqual(new_vote, vote)
        self.assertEqual(new_vote.content_object, reference)

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

    def test_manager_not_archived(self):
        """The default manager's ``not_archived()`` method should return all
            non-archived references."""
        # Some archived references must exist for this test to make sense.
        expected = Reference.objects.filter(is_archived=False)
        self.assertTrue(expected.exists())

        actual = Reference.objects.not_archived()
        self.assertEqual(len(actual), len(expected))
        self.assertFalse(any(r.is_archived for r in actual))

    def test_score_archived_votes(self):
        """The reference's score shouldn't include archived votes."""
        reference = Reference.objects.get(pk=1)
        expected = ReferenceVote.objects.get_for_instance(reference).count()
        self.assertEqual(reference.score, expected)
