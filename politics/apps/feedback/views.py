# coding=utf-8
from django.http import HttpResponse, HttpResponseBadRequest
from politics.apps.feedback.tasks import send_feedback_email


def feedback(request):
    """A REST resource for submitting feedback."""
    if request.method != "POST":
        return HttpResponse(status=405)

    feedback = request.POST.get("feedback")
    url = request.POST.get("url")
    user = request.user

    if feedback:
        user_pk = None if request.user.is_anonymous() else user.pk
        send_feedback_email.delay(feedback, url, user_pk)
        return HttpResponse()

    return HttpResponseBadRequest()
