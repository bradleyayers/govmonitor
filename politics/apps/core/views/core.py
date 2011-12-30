# coding=utf-8
from ..forms import LoginForm, UserForm
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from politics.utils.decorators import render_to_template


@render_to_template("core/log_in.html")
def log_in(request):
    """Displays log in options (Facebook, etc.), handles log in attempts."""
    form = LoginForm()
    if request.method == "POST":
        form = LoginForm(request.POST)

        if form.is_valid():
            form.login(request)
            return redirect(request.GET.get("next") or "core:home")

    next = ""
    if "next" in request.GET:
        next = "?next=%s" % request.GET["next"]

    return {"form": form, "next": next}


def log_out(request):
    """Log the user out.

    This method simply delegates to auth's ``logout()`` view, redirecting to
    the same page. We define this "wrapper" view to simplify ``urls.py``.
    """
    from django.contrib.auth.views import logout as base_logout
    return base_logout(request, next_page=request.get_full_path())


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


@login_required
@render_to_template("core/settings.html")
def settings(request):
    return {}
