# coding=utf-8
from politics.apps.core.forms import ReferenceForm
from politics.apps.core.models import Reference, View
from politics.apps.view_counts.decorators import record_view
from politics.utils.decorators import render_to_template, slug_url
from random import random
import reversion


@slug_url(View)
@record_view
@render_to_template("core/views/show.html")
def show(request, view):
    """Shows information about a :class:`View`."""
    form = ReferenceForm()
    if request.method == "POST" and request.user.is_authenticated():
        instance = Reference(author=request.user, view=view)
        form = ReferenceForm(request.POST, instance=instance)

        if form.is_valid():
            # Version the reference.
            with reversion.create_revision():
                reversion.set_user(request.user)
                form.save()

            form = ReferenceForm()

    # Should we show current or archived references?
    show_current = request.GET.get("archived") != "1"

    if show_current:
        references = view.reference_set.not_archived()

        # Retrieve the reference selected by the user.
        reference_vote = view.get_vote_for_user(request.user)
        selected_reference = getattr(reference_vote, "content_object", None)
    else:
        references = view.reference_set.filter(is_archived=True)
        selected_reference = None

    # Sort the references in descending order of score. Break ties between
    # references by ordering randomly (taking advantage of tuple comparisons).
    references = sorted(references, None, lambda r: (r.score, random()), True)

    return {
        "form": form,
        "references": references,
        "selected_reference": selected_reference,
        "show_current": show_current,
        "view": view
    }
