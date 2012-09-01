# coding=utf-8
from ..forms import LoginForm, UserForm
from ..models import Issue, Party, Reference, Tag, View
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from haystack.query import SearchQuerySet
import logging
from politics.utils.decorators import render_to_template
from politics.utils.paginator import Paginator
from politics.utils.views import simple_view


@render_to_template("core/about.html")
def about(request):
    """The about page."""
    return {
       "issues": Issue.objects.all(),
       "parties": Party.objects.all(),
       "references": Reference.objects.all(),
    }


contact = simple_view("core/contact.html")
faq = simple_view("core/faq.html")


@render_to_template("core/log_in.html")
def log_in(request):
    """The log in page."""
    form = LoginForm()
    if request.method == "POST":
        form = LoginForm(request.POST)

        if form.is_valid():
            form.login(request)
            return redirect(request.GET.get("next", "core:home"))

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


@require_POST
def request(request):
    """Sends a topic request.

    If a user performs a search and isn't happy with the results, they can
    request to be notified when information is added. This view handles request.
    """
    required = {"contact", "query"}
    if set(request.POST.keys()) & required != required:
        return HttpResponseBadRequest()

    username = "An anonymous user"
    if request.user.is_authenticated():
        username = request.user.get_full_name()

    logging.getLogger("email").info("User Request", extra={"body":
        "%s (%s) wants to be notified about \"%s\"." % (
            username, request.POST["contact"], request.POST["query"]
        )
    })

    return HttpResponse()


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

    if len(results) == 0:
        username = "An anonymous user"
        if not request.user.is_anonymous():
            username = request.user.get_full_name()

        logging.getLogger("email").info("Failed Search", extra={"body":
            "%s searched for \"%s\", but no results were found." % (
                username, query
            )
        })

    return {
        "issues": issues,
        "page": Paginator(issues, 25).page(request.GET.get("page", 1)),
        "query": query,
        "tags": (tags + related_tags)[:20]
    }


@login_required
@render_to_template("core/settings.html")
def settings(request):
    return {}