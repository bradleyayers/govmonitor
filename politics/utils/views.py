# coding=utf-8
from .decorators import render_to_template
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.urlresolvers import reverse


def login_path(next_page=None):
    """Returns the path to the login page with an optional "next" argument."""
    redirect_argument = "?{0}={1}".format(REDIRECT_FIELD_NAME, next_page)
    return reverse("core:login") + (redirect_argument if next_page else "")


def simple_view(template):
    """Returns a view function that renders to the given template.

    .. code-block::

        my_view = simple_view("core/template.html")

    :param template: The template to render to.
    :type  template: ``str``
    :returns: A view function that renders ``template``.
    :rtype: ``function``
    """
    @render_to_template(template)
    def view(request):
        return {}

    return view
