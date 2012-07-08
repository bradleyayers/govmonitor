# coding=utf-8
from .forms import VoteForm
from .models import Vote
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
import json
import logging
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
    def _build_response(status=200):
        score = instance.__class__.objects.get(pk=instance.pk).score
        return HttpResponse(json.dumps({"score": score}),
                mimetype="application/json", status=status)

    # Either way, their current vote(s) are archived. We need to actually call
    # save() to trigger the post_save signal which updates the object's score.
    votes = Vote.objects.get_for_instance(instance)
    for vote in votes.filter(author=request.user):
        vote.is_archived = True
        vote.save()

    if request.method == "DELETE":
        return _build_response()

    if request.method == "POST":
        vote = Vote(author=request.user, content_object=instance)
        form = VoteForm(request.POST, instance=vote)

        if form.is_valid():
            vote = form.save()
            logging.getLogger("email").info("New Vote", extra={"body":
                "%s voted %s %d %s." % (
                    request.user.get_full_name(),
                    instance.__class__.__name__,
                    instance.pk,
                    vote.type
                )
            })

            return _build_response(201)
        else:
            return HttpResponseBadRequest()
