# coding=utf-8
from django.conf import settings
from django.core.mail import send_mail
from django.template import Context
from django.template.loader import get_template
from djcelery_transactions import task
from politics.apps.comments.models import Comment


@task(ignore_result=True)
def send_comment_notification_emails(comment_pk, subject, template, users):
    """Sends comment notification emails to a set of users using a template.

    ``subject`` may contain a number of format specifiers into which variables
    will be substituted. The following list details those that are available:

    * ``author_name``: The full name of the comment's author.

    Similarly, several context variables are available within the template:

    * ``comment``: The comment that was posted—the subject of the email.

    :param comment_pk: The ID of the comment that was posted.
    :type  comment_pk: ``int``
    :param    subject: The subject template to use for the emails.
    :type     subject: ``str``
    :param   template: The message template to use for the emails.
    :type    template: ``str``
    :param      users: The users who are to be emailed.
    :type       users: *iterable*
    """
    comment = Comment.objects.get(pk=comment_pk)
    message = get_template(template).render(Context({"comment": comment}))
    subject = subject.format(author_name=comment.author.get_full_name())

    for user in users:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, (user.email,))
