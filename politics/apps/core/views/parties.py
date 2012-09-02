# coding: utf-8
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect
import logging
from politics.apps.core.forms import PartyForm
from politics.apps.core.models import Issue, Party, View
from politics.apps.view_counts.decorators import record_view
from politics.utils.decorators import render_to_template, pk_url, slug_url
import re
import reversion


@login_required
@slug_url(Party, required=False)
@render_to_template("core/parties/form.html")
def form(request, party, parent=None):
    """
    :param request: The HTTP request.
    :type  request: ``django.http.HttpRequest``
    :param   party: The party or ``None``.
    :type    party: ``politics.apps.core.models.Party`` or ``None``
    :param  parent: The default ``parent`` value (used for child parties).
    :type   parent: ``politics.apps.core.models.Party`` or ``None``
    """
    initial = {}
    if parent is not None:
        initial["parent"] = parent

    form = PartyForm(initial=initial, instance=party)

    if request.method == "POST":
        form = PartyForm(request.POST, request.FILES, initial=initial,
                instance=party)

        if form.is_valid():
            with reversion.create_revision():
                reversion.set_user(request.user)
                party = form.save()

            logging.getLogger("email").info("New Party", extra={"body":
                "%s created a party.\n\nhttp://govmonitor.org%s" % (
                    request.user.get_full_name(),
                    reverse("core:parties:show", args=(party.pk, party.slug))
                )
            })

            return redirect("core:parties:show", party.pk, party.slug)

    return {"form": form}


@render_to_template("core/parties/list.html")
def list(request):
    """Show a list of all parties."""
    # Returns the key by which a party is to be sorted.
    def _party_key(party):
        return re.sub("^the", "", party.name.lower()).strip()

    # Only show "root" parties (not sub-parties).
    parties = sorted(Party.objects.filter(tree_level=0), key=_party_key)

    average_view_percentage = sum(p.percentage_views_known for p in parties)
    average_view_percentage = float(average_view_percentage) / len(parties)

    return {
        "average_view_percentage": average_view_percentage,
        "parties": parties
    }


@login_required
@slug_url(Party)
def new_child(request, party):
    """Create a new party with the parent field pre-filled."""
    return form(request, parent=party)


@slug_url(Party)
@record_view
@render_to_template("core/parties/show.html")
def show(request, party):
    """Show information about a ``Party``."""
    tab = request.GET.get("tab", "views")
    if tab not in ("branches", "views"):
        tab = "views"

    party_similarities = party.partysimilarity_set.not_archived()
    party_similarities = party_similarities.order_by("-similarity")

    return {
        "branches": party.get_children(),
        "party": party,
        "party_similarities": party_similarities,
        "tab": tab,
        "views": party.view_set.order_by("-notability", "issue__name")
                .exclude(stance=View.UNKNOWN)
    }
