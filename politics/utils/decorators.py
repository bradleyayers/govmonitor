# coding=utf-8
from django.core.urlresolvers import resolve
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template import RequestContext
from django.views.decorators.http import require_http_methods
from functools import wraps
import json


def pk_url(model):
    """A decorator for Django views with "primary key" URLs.

    Such URLs include a primary key which can be used to retrieve a specific
    model instance of the given type (``model``), which is then passed to the
    view. If no object can be found, 404 Not Found is returned.

    .. code-block:: python

        @pk_url(MyModel)
        def view(request, instance):
            # ...

    The primary key must be captured in the ``pk`` capture group.

    .. code-block:: python

        urlpatterns("",
            url(r"^(?P<pk>\d+)/", view, name="view"),
        )

    :param model: The model on which lookups are to be performed.
    :type  model: ``django.db.models.base.ModelBase``
    """
    def inner(function):
        @wraps(function)
        def wrapper(request, pk, *args, **kwargs):
            instance = get_object_or_404(model, pk=pk)
            return function(request, instance, *args, **kwargs)

        return wrapper

    return inner


def render_json(function):
    """A decorator for Django views that renders output as JSON.

    If the view returns an ``HttpResponse``, it is returned unchanged.
    """
    @wraps(function)
    def wrapper(request, *args, **kwargs):
        # Pass finished responses straight through.
        output = function(request, *args, **kwargs)
        if isinstance(output, HttpResponse):
            return output

        return HttpResponse(content=json.dumps(output, separators=(",", ":")),
                            mimetype="application/json")

    return wrapper


def render_to_template(template):
    """A decorator for Django views that renders a context in a template.

    If the view returns a ``dict``, it will be used as the context when
    rendering ``template``; anything else will be returned unchanged.
    """
    def inner(function):
        @wraps(function)
        def wrapper(request, *args, **kwargs):
            output = function(request, *args, **kwargs)
            if not isinstance(output, dict):
                return output

            return render_to_response(
                    template, output, context_instance=RequestContext(request))

        return wrapper

    return inner


def require_authenticated(function):
    """A decorator for Django views that ensures that the user is logged in.

    :returns: The result of invoking ``function`` if the user is logged in;
              otherwise 401 Unauthorized.
    :rtype: ``django.http.HttpResponse``
    """
    @wraps(function)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated():
            return function(request, *args, **kwargs)
        else:
            return HttpResponse(status=401)

    return wrapper


# Django only provides GET and POST decorators.
require_DELETE = require_http_methods(["DELETE"])
require_DELETE.__doc__ = """A view decorator that only allows DELETE requests.

Returns 405 Method Not Allowed for any other method.
"""


def slug_url(model):
    """A decorator for Django views with "slug" URLs.

    A slug URL includes a primary key and slug (e.g. ``/objects/1/name/``).
    These are used to retrieve a model instance of the given type (``model``),
    which is passed to the view. If no object is found, returns 404 Not Found;
    if the slug is incorrect, a redirect to the URL with the correct slug.

    .. code-block:: python

        @slug_url(MyModel)
        def view(request, instance):
            # ...

    The primary key must be captured in the ``pk`` capture group, the slug in
    the ``slug`` capture group. See the following example URL patterns:

    .. code-block:: python

        urlpatterns("",
            url(r"^(?P<pk>\d+)/(?P<slug>[a-z0-0_-]*)/$", view, name="view"),
        )

    :param model: The model on which lookups are to be performed.
    :type  model: ``django.db.models.base.ModelBase``
    """
    def inner(function):
        @wraps(function)
        def wrapper(request, pk, slug, *args, **kwargs):
            instance = get_object_or_404(model, pk=pk)

            # Is the slug right?
            if slug != instance.slug:
                match = resolve(request.get_full_path())
                kwargs = {"pk": instance.pk, "slug": instance.slug}
                return redirect(match.view_name, **kwargs)

            return function(request, instance, *args, **kwargs)

        return wrapper

    return inner
