# coding=utf-8
from ..forms import ReferenceForm
from ..models import Reference, View
from politics.utils.decorators import render_to_template, slug_url
from random import random
import reversion


@slug_url(View)
@render_to_template("core/views/show.html")
def show(request, view):
    """Shows information about a :class:`View`."""
    form = None
    if request.user.is_authenticated():
        form = ReferenceForm()

        # Are they trying to add a reference?
        if request.method == "POST":
            instance = Reference(author=request.user, view=view)
            form = ReferenceForm(request.POST, instance=instance)

            if form.is_valid():
                with reversion.create_revision():
                    reversion.set_user(request.user)
                    form.save()

                form = ReferenceForm()

    # Retrieve the view's non-archived references in descending order of score.
    # Break ties between references with the same score by ordering randomly.
    references = view.reference_set.not_archived()
    references = sorted(references, None, lambda r: (r.score, random()), True)

    # Pass their vote through.
    selected_reference = None
    if request.user.is_authenticated():
        vote = view.get_vote_for_user(request.user)
        selected_reference = vote.content_object if vote else None

    return {
        "form": form,
        "references": references,
        "selected_reference": selected_reference,
        "view": view
    }
