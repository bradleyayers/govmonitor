# coding=utf-8
from django.http import Http404, HttpResponse, HttpResponseNotFound
from django.template import loader, RequestContext
from functools import wraps
import json


def api(template, compress=True):
    """A view decorator that renders a JSON template using the returned context.

    If the query string contains a ``callback`` parameter, it is JSONP and the
    response will be a call to the named function, passing the rendered JSON.

    If the view raises an ``Http404``, returns an empty 404 Not Found response.

    :param template: The template to render.
    :type  template: ``str``
    :param compress: Whether whitespace should be stripped from the JSON.
    :type  compress: ``boolean``
    """
    def inner(view):
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            try:
                context = view(request, *args, **kwargs)
            except Http404:
                # We don't want to use the standard HTML 404 page.
                return HttpResponseNotFound(mimetype="application/json")

            # Pass pre-built requests through.
            if not isinstance(context, dict):
                return context

            content = loader.render_to_string(template, context,
                    context_instance=RequestContext(request))

            if compress:
                content = json.dumps(json.loads(content),
                        separators=(",", ":"))

            # JSONP support.
            callback = request.GET.get("callback")
            mimetype = "application/json"

            if callback is not None:
                content = "%s(%s)" % (callback, content)
                mimetype = "application/javascript"

            return HttpResponse(content, mimetype=mimetype)

        return wrapper

    return inner