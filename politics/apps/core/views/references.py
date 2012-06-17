# coding=utf-8
from ..forms import ReferenceForm
from ..models import Reference
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from politics.apps.comments.views import comments as base_comments
from politics.apps.votes.views import votes as base_votes
from politics.utils.decorators import pk_url, render_to_template
import reversion


@pk_url(Reference)
def comments(request, reference):
    """Create/read reference comments.

    :param   request: The HTTP request that was made.
    :type    request: ``django.http.HttpRequest``
    :param reference: The reference being commented on.
    :type  reference: :class:`Reference`
    """
    return base_comments(request, reference)


@login_required
@pk_url(Reference)
@render_to_template("core/references/edit.html")
def edit(request, reference):
    """Edit a reference.

    :param   request: The HTTP request that was made.
    :type    request: ``django.http.HttpRequest``
    :param reference: The reference being edited.
    :type  reference: :class:`Reference`
    """
    form = ReferenceForm(instance=reference)

    if request.method == "POST":
        form = ReferenceForm(request.POST, instance=reference)

        if form.is_valid():
            # Version the reference.
            with reversion.create_revision():
                reversion.set_user(request.user)
                form.save()

            view = reference.view
            return redirect("core:views:show", pk=view.pk, slug=view.slug)

    return {"form": form, "reference": reference}


@pk_url(Reference)
def votes(request, reference):
    """Create/delete votes.

    :param  request: The HTTP request that was made.
    :type   request: ``django.http.HttpRequest``
    :param reference: The reference being voted on.
    :type  reference: :class:`Reference`
    """
    base_votes(request, reference)
