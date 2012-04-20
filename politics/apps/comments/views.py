# coding=utf-8
from django.http import HttpResponse
import json
from politics.apps.comments.models import Comment
from politics.apps.comments.forms import CommentForm
from politics.utils.decorators import render_json


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
            return HttpResponse(json.dumps(comment.to_json()), status=201)
        else:
            return HttpResponse(status=400)
