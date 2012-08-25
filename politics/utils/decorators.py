# coding=utf-8
from django.core.urlresolvers import resolve
from django.http import Http404, HttpResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template import loader, RequestContext
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
        try:
            output = function(request, *args, **kwargs)
        except Http404:
            # We don't want to display the HTML 404 page.
            return HttpResponseNotFound(mimetype="application/json")

        # Pass pre-built reponses straight through.
        if isinstance(output, HttpResponse):
            return output

        return HttpResponse(content=json.dumps(output, separators=(",", ":")),
                            mimetype="application/json")

    return wrapper


def render_to_template(template):
    """A view decorator that renders a template using the returned context.

    If the view returns a ``dict``, it will be used as the context when
    rendering ``template``; anything else will be returned unchanged.

    :param template: The template to render.
    :type  template: ``str``
    """
    def inner(view):
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            context = view(request, *args, **kwargs)

            # Pass pre-built responses through.
            if not isinstance(context, dict):
                return context

            return render_to_response(template, context,
                    context_instance=RequestContext(request))

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


def slug_url(model, required=True, pk_key="pk", slug_key="slug"):
    """A decorator for Django views with "slug" URLs.

    A slug URL includes a primary key and slug (e.g. ``/objects/1-name/``).
    These are used to retrieve a model instance of the given type (``model``),
    which is passed to the view.

    If ``required`` is ``True`` and no matching model is found, 404 Not Found is
    return. If ``slug`` is incorrect, a permanent redirect to the correct URL.

    If ``required`` is ``False``, the primary key and slug may be ``None`` and
    the view will be executed as normal, with ``None`` for the model argument.

    .. code-block:: python

        @slug_url(MyModel)
        def view(request, instance):
            # ...

    By default, this decorator looks for "pk" and "slug" in the view's keyword
    arguments. Specify different keys by passing "pk_key" or "slug_key" values.

    .. code-block:: python

        urlpatterns("",
            url(r"^(?P<pk>\d+)/(?P<slug>[a-z0-9_-]*)/$", defaults),
            url(r"^(?P<my_pk>\d+)/(?P<my_slug>[a-z0-9_-]*)/$" custom)
        )

        @slug_url(MyModel)
        def defaults(request, model):
            # ...

        @slug_url(MyModel, pk_key="my_pk", slug_key="my_slug")
        def custom(request, model):
            # ...

    :param    model: The model on which lookups are to be performed.
    :type     model: ``django.db.models.base.ModelBase``
    :param required: Whether ``pk`` and ``slug`` are required.
    :type  required: ``bool``
    :param   pk_key: The name of the primary key argument.
    :type    pk_key: ``str``
    :param slug_key: The name of the slug argument.
    :type  slug_key: ``str``
    """
    def inner(function):
        @wraps(function)
        def wrapper(request, *args, **kwargs):
            pk, slug = kwargs.pop(pk_key, None), kwargs.pop(slug_key, None)

            # If it's not required and no data was given, just call the view.
            if required == False and pk is None and slug is None:
                return function(request, *(args + (None,)), **kwargs)

            instance = get_object_or_404(model, pk=pk)

            # Is the slug right?
            if slug != instance.slug:
                match = resolve(request.get_full_path())
                kwargs.update({pk_key: pk, slug_key: instance.slug})
                return redirect(match.view_name, permanent=True, **kwargs)

            return function(request, *(args + (instance,)), **kwargs)

        return wrapper

    return inner