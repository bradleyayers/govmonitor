# coding=utf-8
from celery.task import task
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template import Context
from django.template.loader import get_template


@task(ignore_result=True)
def send_feedback_email(feedback, url, user_pk):
    """Sends an email to all admins containing the new feedback.

    :param feedback: The feedback that was given.
    :type  feedback: ``str``
    :param      url: The URL the user was on when they submitted the feedback.
    :type       url: ``str``
    :param  user_pk: The ID of the user who submitted the feedback or ``None``
                     if they weren't logged in (it was submitted anonymously).
    :type   user_pk: ``int`` or ``None``
    """
    subject = "New Feedback"
    message = get_template("feedback/mail/feedback.txt").render(Context({
       "user": None if user_pk is None else User.objects.get(pk=user_pk),
       "feedback": feedback,
       "url": url,
    }))

    for admin in settings.ADMINS:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, (admin[1],))
