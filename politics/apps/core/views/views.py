# coding=utf-8
from politics.apps.core.forms import ReferenceForm
from politics.apps.core.managers import ViewManager
from politics.apps.core.models import Issue, Party, Reference, View
from politics.apps.view_counts.decorators import record_view
from politics.utils.decorators import render_to_template, slug_url
from random import random
import reversion


@slug_url(Issue, pk_key="issue_pk", slug_key="issue_slug")
@slug_url(Party, pk_key="party_pk", slug_key="party_slug")
@render_to_template("core/views/show.html")
def show(request, issue, party):
    """Shows information about a :class:`View`.

    The view may not yet be present in the database.

    :param request: The HTTP request.
    :type  request: ``django.http.HttpRequest``
    :param   issue: The issue.
    :type    issue: ``politics.apps.core.models.Issue``
    :param   party: The party.
    :type    party: ``politics.apps.core.models.Party``
    """
    reference_form = ReferenceForm()
    view = ViewManager().get_view(issue, party)

    # Are they trying to create a reference?
    if request.method == "POST" and request.user.is_authenticated():
        view.save() # The view must exist in the database.
        instance = Reference(author=request.user, view=view)
        reference_form = ReferenceForm(request.POST, instance=instance)

        if reference_form.is_valid():
            # Version the reference.
            with reversion.create_revision():
                reversion.set_user(request.user)
                reference_form.save()

            reference_form = ReferenceForm()

    # The currently winning reference.
    current_reference = view.get_current_reference()
    current_reference_pk = getattr(current_reference, "pk", None)

    # Sort the references in descending order of score. Break ties between
    # references by ordering randomly (taking advantage of tuple comparisons).
    references = view.reference_set.exclude(pk=current_reference_pk)
    references = sorted(references, None, lambda r: (r.score, random()), True)

    return {
        "current_reference": current_reference,
        "reference_form": reference_form,
        "references": references,
        "view": view
    }
