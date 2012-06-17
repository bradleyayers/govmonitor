# coding=utf-8
from .forms import VoteForm
from .models import Vote
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from politics.utils.decorators import require_authenticated


@require_authenticated
@require_http_methods(["DELETE", "POST"])
def votes(request, instance):
    """A generic, RESTful view for voting on an object.

    :param  request: The HTTP request that was made.
    :type   request: ``djang.http.HttpRequest``
    :param instance: The object to operated on.
    :type  instance: ``django.db.models.Model``
    """
    # Either way, their current vote is archived.
    votes = Vote.objects.get_for_instance(instance)
    votes.filter(author=request.user).update(is_archived=True)

    if request.method == "DELETE":
        return HttpResponse()

    if request.method == "POST":
        vote = Vote(author=request.user, content_object=instance)
        form = VoteForm(request.POST, instance=vote)

        if form.is_valid():
            vote = form.save()
            return HttpResponse(status=201)
        else:
            return HttpResponseBadRequest()
