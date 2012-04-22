# coding=utf-8
from django.conf import settings
from django.core.mail import send_mail
from django.template import Context, Template
from django.template.loader import get_template
from djcelery_transactions import task
from politics.apps.comments.models import Comment


@task(ignore_result=True)
def send_reply_notification_emails(reply_pk):
    """Emails participants in a comment thread, notifying them of a new reply.

    :param reply_pk: The ID of the comment that was posted.
    :type  reply_pk: ``int``
    """
    reply = Comment.objects.get(pk=reply_pk)

    # Fetch the users who participated in the thread before the reply; we only
    # want to email these users to avoid the race condition with newer comments.
    earlier_comments = Comment.objects.get_for_instance(reply.content_object)
    earlier_comments = earlier_comments.exclude(pk__gte=reply.pk)
    earlier_authors = {c.author for c in earlier_comments} - {reply.author}

    # Render the email template.
    context = Context({"reply": reply})
    message = get_template("comments/mail/reply.txt").render(context)
    subject = "{0} replied to your comment on AusPolitics!".format(
            reply.author.get_full_name())

    for author in earlier_authors:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [author.email])
