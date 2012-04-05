# coding=utf-8
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from haystack.query import SearchQuerySet
from politics.apps.core.forms import IssueForm
from politics.apps.core.models import Issue, View
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
@render_to_template("core/issues/form.html")
def form(request, pk=None):
    # If we're editing an Issue, pk will be set.
    issue = None
    if pk is not None:
        issue = get_object_or_404(Issue, pk=pk)

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

            return redirect("core:issues:show", pk=issue.pk, slug=issue.slug)

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


@slug_url(Issue)
@render_to_template("core/issues/show.html")
def show(request, issue):
    """Display information about an issue."""
    related_issues = SearchQuerySet().models(Issue).more_like_this(issue)
    related_issues = [result.object for result in related_issues]

    # Pass stance counts through for the pie chart.
    views = issue.view_set.select_related().order_by("party__name")
    stances = [(s[1], views.filter(stance=s[0]).count()) for s in View.STANCE_CHOICES]

    return {
        "issue": issue,
        "related_issues": related_issues,
        "stances": stances,
        "views": views,
    }
