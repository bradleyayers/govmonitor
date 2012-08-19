# coding=utf-8
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect
from haystack.query import SearchQuerySet
import logging
from politics.apps.core.forms import IssueForm
from politics.apps.core.managers import ViewManager
from politics.apps.core.models import Issue, View
from politics.apps.view_counts.decorators import record_view
from politics.utils.decorators import render_to_template, slug_url
from politics.utils.paginator import Paginator
import reversion


# The number of parties that should be displayed in the view tables. The
# view_table template tag will select the parties with the most information.
NUMBER_OF_PARTIES = 5


@render_to_template("core/issues/active.html")
def active(request):
    """Shows active issues: those that have been updated recently."""
    issues = Issue.objects.order_by("-updated_at")
    page = Paginator(issues, 25).page(request.GET.get("page", 1))

    # Extract the set of tags from the most recently updated issues.
    tags = sum((list(issue.tags.all()) for issue in issues), [])
    tags = sorted(set(tags), key=tags.index)

    return {"number_of_parties": NUMBER_OF_PARTIES, "page": page, "tags": tags}


@login_required
@slug_url(Issue, required=False, pk_key="issue_pk", slug_key="issue_slug")
@render_to_template("core/issues/form.html")
def form(request, issue):
    form = IssueForm(instance=issue)

    if request.method == "POST":
        form = IssueForm(request.POST, instance=issue)

        if form.is_valid():
            with reversion.create_revision():
                reversion.set_user(request.user)
                issue = form.save()

                # django-reversion detects changes by listening for post_save
                # signals; thus it doesn't get up-to-date tags as they're saved
                # after the Issue. Call save to fire a signal and fix this.
                issue.save()

            logging.getLogger("email").info("Issue Saved", extra={"body":
                "%s %s an issue.\n\nhttp://govmonitor.org%s" % (
                    request.user.get_full_name(), "saved",
                    reverse("core:issues:show", args=(issue.pk, issue.slug))
                )
            })

            return redirect("core:issues:show", issue_pk=issue.pk,
                    issue_slug=issue.slug)

    return {"form": form}


@render_to_template("core/issues/popular.html")
def popular(request):
    """Shows issues that have been marked as popular."""
    # Fetch issues that are marked as popular and paginate them.
    issues = Issue.objects.filter(is_popular=True).order_by("name")
    page = Paginator(issues, 25).page(request.GET.get("page", 1))

    return {
        "number_of_parties": NUMBER_OF_PARTIES,
        "page": page,
        "tags": Issue.common_tags(page.object_list)
    }


@slug_url(Issue, pk_key="issue_pk", slug_key="issue_slug")
@record_view
@render_to_template("core/issues/show.html")
def show(request, issue):
    """Display information about an issue."""
    related_issues = SearchQuerySet().models(Issue).more_like_this(issue)
    related_issues = [result.object for result in related_issues]

    # Retrieve the views of root parties.
    views = ViewManager().get_views_for_issue(issue)
    views = filter(lambda v: v.party.tree_level == 0, views)
    views = sorted(views, key=lambda view: view.party.name.lower())

    stances = []
    for stance in View.STANCE_CHOICES:
        count = sum(1 for view in views if view.stance == stance[0])
        stances.append((stance[1], count))

    return {
        "issue": issue,
        "related_issues": related_issues,
        "stances": stances,
        "views": views
    }
