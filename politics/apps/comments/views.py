# coding=utf-8
from django.db import transaction
from django.http import HttpResponse, HttpResponseBadRequest
import json
from politics.apps.comments.models import Comment
from politics.apps.comments.forms import CommentForm
from politics.apps.comments.tasks import send_reply_notification_emails
from politics.utils.decorators import pk_url, render_json, require_authenticated
import reversion


@pk_url(Comment)
@require_authenticated
@transaction.commit_on_success
def comment(request, instance):
    """A RESTful view for deleting/editing comments.

    :param  request: The HTTP request that was made.
    :type   request: ``django.http.HttpRequest``
    :param instance: The comment that is to be operated on.
    :type  instance: ``politics.apps.comments.models.Comment``
    """
    # They must be the author of the comment.
    if request.user != instance.author:
        return HttpResponse(status=403)

    if request.method == "DELETE":
        with reversion.create_revision():
            instance.is_deleted = True
            instance.save()

        return HttpResponse(status=200)
    elif request.method == "PUT":
        # Deleted comments can't be edited.
        if instance.is_deleted:
            return HttpResponseBadRequest()

        form = CommentForm(request.PUT, instance=instance)

        if form.is_valid():
            with reversion.create_revision():
                instance = form.save()

            return HttpResponse(json.dumps(instance.to_json()))
        else:
            return HttpResponseBadRequest()

    # Method Not Allowed
    return HttpResponse(status=405)


@transaction.commit_on_success
def comments(request, instance):
    """A generic, RESTful view for creating/reading comments on an object.

    .. code-block:: python

        from politics.apps.comments.views import comments as base_comments


        @pk_url(MyModel)
        def comments(request, my_model):
            return base_comments(request, my_model)

    :param  request: The HTTP request that was made.
    :type   request: ``django.http.HttpRequest``
    :param instance: The object to operate on.
    :type  instance: ``django.db.models.Model``
    """
    if request.method == "POST":
        # The client must be authenticated to create a comment.
        if not request.user.is_authenticated():
            return HttpResponse(status=401)

        comment = Comment(author=request.user, content_object=instance)
        form = CommentForm(request.POST, instance=comment)

        if form.is_valid():
            comment = form.save()
            send_reply_notification_emails.delay(comment.pk)
            return HttpResponse(json.dumps(comment.to_json()), status=201)
        else:
            return HttpResponseBadRequest()

    # Method Not Allowed
    return HttpResponse(status=405)
