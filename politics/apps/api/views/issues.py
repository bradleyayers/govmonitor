# coding=utf-8
from ..decorators import api
from politics.apps.core.models import Issue, View
from politics.utils.decorators import pk_url


@api("api/issues/show.json")
@pk_url(Issue)
def show(request, issue):
    """Returns information about a single issue."""
    return {
        "issue": issue,
        "views": issue.view_set.exclude(stance=View.UNKNOWN)
    }