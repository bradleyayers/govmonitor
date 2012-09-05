# coding=utf-8
from politics.apps.core.models import Election
from politics.utils.decorators import render_to_template, slug_url


@render_to_template("core/elections/list.html")
def list(request):
    """Show a list of elections.

    :param request: The HTTP request.
    :type  request: ``django.http.HttpRequest``
    """
    return {"elections": Election.objects.order_by("held_on")}


@render_to_template("core/elections/show.html")
@slug_url(Election)
def show(request, election, tab="issues"):
    """Show information about an election.

    :param  request: The HTTP request.
    :type   request: ``django.http.HttpRequest``
    :param election: The election.
    :type  election: ``politics.apps.core.models.Election``
    :param      tab: The tab to display ("issues" or "issues").
    :type       tab: ``str``
    """
    return {
        "election": election,
        "issues": election.issues.all(),
        "parties": election.parties.all(),
        "tab": tab
    }