# coding=utf-8
from ..forms import ReferenceForm
from ..models import Reference
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods, require_POST
from politics.apps.comments.views import comments as base_comments
from politics.utils.decorators import (pk_url, render_json, render_to_template,
                                       require_authenticated)
import reversion


@login_required
@require_POST
@pk_url(Reference)
def archive(request, reference, archive=True):
    """Archive or unarchive a reference.

    :param   request: The HTTP request that was made.
    :type    request: ``django.http.HttpRequest``
    :param reference: The reference that is to be (un)archived.
    :type  reference: :class:`Reference`
    :param   archive: If ``True``, ``reference`` will be archived; if
                      ``False``, it will be unarchived. Set in the URLconf.
    :type    archive: ``bool``
    """
    reference.is_archived = archive
    reference.save()

    kwargs = {"pk": reference.view.pk, "slug": reference.view.slug}
    return HttpResponseRedirect(reverse("core:views:show", kwargs=kwargs) +
                                ("" if archive else "?archived=1"))


@pk_url(Reference)
def comments(request, reference):
    """Create/read reference comments.

    :param   request: The HTTP request that was made.
    :type    request: ``django.http.HttpRequest``
    :param reference: The reference described by the primary key in the URL.
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
