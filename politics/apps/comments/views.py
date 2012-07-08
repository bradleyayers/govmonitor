# coding=utf-8
from django.http import HttpResponse, HttpResponseBadRequest
import json
import logging
from politics.apps.comments.models import Comment
from politics.apps.comments.forms import CommentForm
from politics.utils.decorators import pk_url, require_authenticated
import reversion


@pk_url(Comment)
@require_authenticated
def comment(request, instance):
    """A RESTful view for deleting/editing comments.

    :param  request: The HTTP request that was made.
    :type   request: ``django.http.HttpRequest``
    :param instance: The comment that is to be operated on.
    :type  instance: ``politics.apps.comments.models.Comment``
    """
    # The client must be the author of the comment.
    if request.user != instance.author:
        return HttpResponse(status=403)

    if request.method == "DELETE":
        with reversion.create_revision():
            instance.is_deleted = True
            instance.save()

        return HttpResponse(json.dumps(instance.to_json()))
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


@require_authenticated
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
        comment = Comment(author=request.user, content_object=instance)
        form = CommentForm(request.POST, instance=comment)

        if form.is_valid():
            with reversion.create_revision():
                comment = form.save()

            logging.getLogger("email").info("New Comment", extra={"body":
                "%s commented on %s %d." % (
                    request.user.get_full_name(),
                    instance.__class__.__name__,
                    instance.pk
                )
            })

            return HttpResponse(json.dumps(comment.to_json()), status=201)
        else:
            return HttpResponseBadRequest()

    # Method Not Allowed
    return HttpResponse(status=405)
