# coding=utf-8
from ..forms import LoginForm, UserForm
from ..models import Issue, Tag
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from haystack.query import SearchQuerySet
from politics.utils.decorators import render_to_template
from politics.utils.paginator import Paginator


@render_to_template("core/about.html")
def about(request):
    """The about page."""
    return {}


@render_to_template("core/contact.html")
def contact(request):
    """The contact page."""
    return {}


@render_to_template("core/log_in.html")
def log_in(request):
    """The log in page."""
    form = LoginForm()
    if request.method == "POST":
        form = LoginForm(request.POST)

        if form.is_valid():
            form.login(request)
            return redirect(request.GET.get("next") or "core:home")

    next_page = ""
    if "next" in request.GET:
        next_page = "?next=%s" % request.GET["next"]

    return {"form": form, "next": next_page}


def log_out(request):
    """Log the user out.

    This method simply delegates to auth's ``logout()`` view, redirecting to
    the same page. We define this "wrapper" view to simplify ``urls.py``.
    """
    from django.contrib.auth.views import logout as base_logout
    return base_logout(request, next_page="/")


@render_to_template("core/register.html")
def register(request):
    """Displays a registration form, handles registration attempts."""
    # If they're already logged in, what are they registering for?
    if request.user.is_authenticated():
        return redirect("core:home")

    form = UserForm(request)
    if request.method == "POST":
        form = UserForm(request, request.POST)

        if form.is_valid():
            # Create the user and log them in.
            user = form.save()
            user = auth.authenticate(username=user.username,
                                     password=form.cleaned_data["password"])
            auth.login(request, user)
            return redirect("core:home")

    return {"form": form}


@render_to_template("core/search.html")
def search(request):
    """The search page."""
    query = request.GET.get("q")

    if not query:
        return redirect("core:home")

    # Search for Issue and Tags matching the query.
    results = SearchQuerySet().auto_query(query).load_all()
    issues = [result.object for result in results.models(Issue)]
    tags = [result.object for result in results.models(Tag)]

    # Extract commons tags that may not be in the search results. Remove
    # duplicates as this is shown below the results (but preserve ordering).
    related_tags = Issue.common_tags(issues)
    related_tags = [tag for tag in related_tags if tag not in tags]

    return {
        "issues": issues,
        "page": Paginator(issues, 25).page(request.GET.get("page", 1)),
        "tags": (tags + related_tags)[:20]
    }


@login_required
@render_to_template("core/settings.html")
def settings(request):
    return {}
