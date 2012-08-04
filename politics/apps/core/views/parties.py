# coding: utf-8
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
import logging
from politics.apps.core.forms import PartyForm
from politics.apps.core.models import Issue, Party, View
from politics.apps.view_counts.decorators import record_view
from politics.utils import group_n
from politics.utils.decorators import render_to_template, pk_url, slug_url
import re


@render_to_template("core/parties/list.html")
def list(request):
    """Show a list of all parties."""
    # Returns the key by which a party is to be sorted.
    def _party_key(party):
        return re.sub("^the", "", party.name.lower()).strip()

    # Only show "root" parties (not sub-parties).
    parties = sorted(Party.objects.filter(tree_level=0), key=_party_key)

    average_view_percentage = sum(p.view_percentage for p in parties)
    average_view_percentage = float(average_view_percentage) / len(parties)

    return {
        "average_view_percentage": average_view_percentage,
        "party_rows": group_n(parties, 2)
    }


@login_required
@render_to_template("core/parties/new.html")
def new(request, parent=None):
    """Create a new party."""
    form = PartyForm(initial={"parent": parent})

    if request.method == "POST":
        form = PartyForm(request.POST, request.FILES)

        if form.is_valid():
            party = form.save()

            logging.getLogger("email").info("New Party", extra={"body":
                "%s created a party.\n\nhttp://govmonitor.org%s" % (
                    request.user.get_full_name(),
                    reverse("core:parties:show", args=(party.pk, party.slug))
                )
            })

            return redirect("core:parties:show", party.pk, party.slug)

    return {"form": form}


@login_required
@pk_url(Party)
def new_child(request, party):
    """Create a new party with the parent field pre-filled."""
    return new(request, party)


@slug_url(Party)
@record_view
@render_to_template("core/parties/show.html")
def show(request, party):
    """Show information about a ``Party``."""
    views = party.view_set.order_by("-notability", "issue__name")

    if request.GET.get("issues") != "unknown":
        views = views.exclude(stance=View.UNKNOWN)
    else:
        views = views.filter(stance=View.UNKNOWN)

    party_similarities = party.partysimilarity_set.not_archived()
    party_similarities = party_similarities.order_by("-similarity")

    return {
        "children": party.get_children(),
        "party": party,
        "party_similarities": party_similarities,
        "view_rows": group_n(views, 2)
    }