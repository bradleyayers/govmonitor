# coding=utf-8
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.urlresolvers import reverse


def login_path(next_page=None):
    """Returns the path to the login page with an optional "next" argument."""
    redirect_argument = "?{0}={1}".format(REDIRECT_FIELD_NAME, next_page)
    return reverse("core:login") + (redirect_argument if next_page else "")
