# coding: utf-8
from ..forms import PartyForm
from ..models import Issue, Party, View
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from politics.utils.decorators import render_to_template, slug_url
from politics.utils.paginator import Paginator
import re


@render_to_template("core/parties/list.html")
def list(request):
    """Show a list of all parties."""
    # Returns the key by which a party is to be sorted.
    def _party_key(party):
        return re.sub("^the", "", party.name.lower()).strip()

    parties = Party.objects.all()
    parties = sorted(parties, key=_party_key)
    average_view_percentage = 0

    for party in parties:
        # Retrieve all information that we have on the party.
        views = party.view_set.exclude(stance=View.UNKNOWN).select_related()

        # Calculate the party's "favourite" tags.
        party.tags = Issue.common_tags(set(view.issue for view in views))

        # Calculate the view percentage.
        issue_count = Issue.objects.count()
        party.view_percentage = float(len(views)) / issue_count * 100
        average_view_percentage += party.view_percentage

    return {
        "average_view_percentage": average_view_percentage / len(parties),
        "parties": parties
    }


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
    if request.GET.get("issues") != "unknown":
        views = views.exclude(stance=View.UNKNOWN)
    else:
        views = views.filter(stance=View.UNKNOWN)

    party_similarities = party.partysimilarity_set.not_archived()
    party_similarities = party_similarities.order_by("-similarity")

    return {
        "party": party,
        "party_similarities": party_similarities,
        "views": views
    }
