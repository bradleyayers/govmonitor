# coding=utf-8
from ..forms import IssueForm
from ..models import Issue, View
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from politics.utils.decorators import render_to_template, slug_url
from politics.utils.paginator import Paginator


# The number of parties that should be displayed in the view tables. The
# view_table template tag will select the parties with the most information.
NUMBER_OF_PARTIES = 5


@render_to_template("core/issues/active.html")
def active(request):
    """Shows active issues: those that have been updated recently."""
    issues = Issue.objects.order_by("-updated_at")
    page = Paginator(issues, 25).page(request.GET.get("page", 1))
    return {"number_of_parties": NUMBER_OF_PARTIES, "page": page}


@login_required
@render_to_template("core/issues/form.html")
def edit(request, pk):
    issue = get_object_or_404(Issue, pk=pk)
    form = IssueForm(instance=issue)

    if request.method == "POST":
        form = IssueForm(request.POST, instance=issue)

        if form.is_valid():
            issue = form.save()
            return redirect("core:issues:show", pk=issue.pk, slug=issue.slug)

    return {"form": form}


@login_required
@render_to_template("core/issues/form.html")
def new(request):
    """Create a new issue."""
    form = IssueForm()

    if request.method == "POST":
        form = IssueForm(request.POST)

        if form.is_valid():
            issue = form.save()
            return redirect("core:issues:show", pk=issue.pk, slug=issue.slug)

    return {"form": form}


@render_to_template("core/issues/popular.html")
def popular(request):
    """Shows issues that have been marked as popular."""
    issues = Issue.objects.filter(is_popular=True).order_by("name")
    page = Paginator(issues, 25).page(request.GET.get("page", 1))
    return {"number_of_parties": NUMBER_OF_PARTIES, "page": page}


@slug_url(Issue)
@render_to_template("core/issues/show.html")
def show(request, issue):
    """Display information about an issue."""
    return {
        "issue": issue,
        "views": issue.view_set.select_related().order_by("party__name")
    }
