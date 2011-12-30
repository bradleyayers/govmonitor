# coding: utf-8
from ..forms import PartyForm
from ..models import Party, Tag
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from politics.utils.decorators import render_to_template, slug_url
from politics.utils.paginator import Paginator


@render_to_template("core/parties/list.html")
def list(request):
    """Show a list of all parties."""
    parties = Party.objects.order_by("name")
    return {"page": Paginator(parties, 25).page(request.GET.get("page", 1))}


@login_required
@render_to_template("core/parties/new.html")
def new(request):
    """Create a new party."""
    form = PartyForm()

    if request.method == "POST":
        form = PartyForm(request.POST)

        if form.is_valid():
            party = form.save()
            return redirect("core:parties:show", party.pk, party.slug)

    return {"form": form}


@slug_url(Party)
@render_to_template("core/parties/show.html")
def show(request, party):
    """Show information about a ``Party``."""
    views = party.view_set.order_by("issue__name")
    page = Paginator(views, 25).page(request.GET.get("page", 1))
    return {"page": page, "party": party}
