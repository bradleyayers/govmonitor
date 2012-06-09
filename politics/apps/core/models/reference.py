# coding=utf-8
from django.contrib.contenttypes import generic
from django.db import models
from politics.apps.core.fields import ScoreField
from politics.apps.core.models import View, Vote
from politics.utils.models import MarkdownField


class Reference(models.Model):
    """A reference to information that clarifies a party's view on an issue.

    If, for example, a political party lists their policies on their website,
    you could reference that page as proof that they support/oppose an issue.

    Each reference has a ``score`` which is an indication of its quality or how
    well it "backs up" the view. This is the number of votes it has received.

    :ivar      author: The user that submitted the reference.
    :type      author: ``django.contrib.auth.models.User``
    :ivar  created_at: When the reference was created.
    :type  created_at: ``datetime.datetime``
    :ivar published_on: When the information itself was published (e.g. when a
                        news article was posted online or printed in the paper).
    :type published_on: ``datetime.date`` or ``None``
    :ivar       score: A cached version of the reference's score. This is
                       updated automagically when its vote set changes.
    :type       score: ``int``
    :ivar      stance: The stance that this reference concerns.
    :type      stance: ``str``
    :ivar        text: An excerpt from the reference in Markdown format (e.g. a
                       quote that clarifies the party's stance). Blank if the
                       reference cannot be adequately summarised in such a way.
    :type        text: ``str``
    :ivar   text_html: The reference's text converted to HTML.
    :type   text_html: ``str``
    :ivar         url: The URL of the reference. May be FTP or HTTP(S).
    :type         url: ``str``
    :ivar        view: The issue/party pair that this reference concerns.
    :type        view: :class:`View`
    :ivar       votes: Votes that have been cast on the reference.
    :type       votes: ``QuerySet`` of :class:`Vote`s
    """

    # Stances that a `Reference` may support.
    STANCE_CHOICES = (
        View.SUPPORT_CHOICE,
        View.OPPOSE_CHOICE,
        View.UNCLEAR_CHOICE,
    )

    author = models.ForeignKey("auth.User")
    created_at = models.DateTimeField(auto_now_add=True)
    published_on = models.DateField(blank=True, null=True)
    score = ScoreField()
    stance = models.CharField(choices=STANCE_CHOICES, max_length=7)
    text = MarkdownField(blank=True, disable=["images"])
    text_html = models.TextField(blank=True)

    # TODO: Support references that aren't webpages.
    # TODO: Should we be validating URLs (ensuring they're online)?
    url = models.URLField(verbose_name="URL")

    view = models.ForeignKey("View")
    votes = generic.GenericRelation(Vote)

    class Meta:
        app_label = "core"
        unique_together = ("view", "url", "stance")

    def __unicode__(self):
        return self.url

    @staticmethod
    def create_author_vote(instance, created, raw, **kwargs):
        """Cast a vote on a newly created reference from its author.

        :param instance: The reference that was saved.
        :type  instance: ``politics.apps.core.models.Reference``
        :param  created: Whether the reference is newly created.
        :type   created: ``bool``
        :param      raw: ``True`` if the reference was created as a result of
                         loading a fixture; ``False`` for a normal save.
        :type       raw: ``bool``
        """
        # Don't bother if we're loading a fixture as it will contain the votes.
        if created and not raw:
            instance.view.cast_vote(instance, instance.author)

    def get_comment_thread_url(self):
        """Returns the absolute path to the reference's comment thread.

        .. note::

            This is the user-facing view's path, not the internal API.

        :returns: The absolute path to the reference's comment thread.
        :rtype: ``str``
        """
        return self.view.get_absolute_url()

    def handle_comment_created(self, comment):
        """Send comment notification emails as necessary.

        Called when a new comment is made on the reference.

        :param comment: The comment that was posted.
        :type  comment: ``politics.apps.comments.models.Comment``
        """
        from politics.apps.comments.tasks import send_comment_notification_emails

        # Email the author of the reference.
        if self.author != comment.author:
            subject = "{author_name} commented on your reference on AusPolitics!"
            send_comment_notification_emails.delay(comment.pk, subject,
                    "core/references/mail/comment.txt", (self.author,))

        # Email participants in the comment thread.
        authors = comment.get_earlier_authors() - {comment.author, self.author}
        subject = "{author_name} replied to your comment on AusPolitics!"
        send_comment_notification_emails.delay(comment.pk, subject,
                "core/references/mail/reply.txt", authors)

    @staticmethod
    def update_view(instance, **kwargs):
        """Update the :class:`View`'s stance.

        :param instance: The :class:`Reference` that was saved or deleted.
                         Careful: it's not in the database for the latter.
        :type  instance: :class:`Reference`
        """
        try:
            instance.view.refresh_stance()
        # Deleting a `View` cascades to its references (here), but, at that
        # point, it doesn't exist any more so we can't update its stance.
        except View.DoesNotExist:
            pass


# Automatically cast a vote on new References from their author.
models.signals.post_save.connect(Reference.create_author_vote, sender=Reference)

# Update views when their references change.
models.signals.post_delete.connect(Reference.update_view, sender=Reference)
models.signals.post_save.connect(Reference.update_view, sender=Reference)
