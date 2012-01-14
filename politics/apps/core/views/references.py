# coding=utf-8
from ..models import Reference, ReferenceVote, Vote
from django.views.decorators.http import require_http_methods
from politics.utils.decorators import (pk_url, render_json,
                                       require_authenticated)


@require_authenticated
@require_http_methods(["DELETE", "POST"])
@pk_url(Reference)
@render_json
def votes(request, reference):
    """Attempts to cast or withdraw a vote on a :class:`Reference`.

    Casting a vote will archive the user's existing vote within the view.

    :param   request: The HTTP request that was made.
    :type    request: ``django.http.HttpRequest``
    :param reference: The reference described by the primary key in the URL.
    :type  reference: :class:`Reference`
    """
    # Either way, their vote is withdrawn.
    reference.view.withdraw_vote(request.user)

    if request.method == "POST":
        reference.view.cast_vote(reference, request.user)

    # Refresh the reference so its score is up to date.
    reference = Reference.objects.get(pk=reference.pk)
    return {"score": reference.score}
