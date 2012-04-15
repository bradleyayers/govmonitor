# coding=utf-8
from .models import View
from functools import wraps


def record_view(function):
    """A view decorator that records the viewing of an object.

    Assumes that the first argument is the request and the second is the object
    being viewed; thus, this decorator should follow ``pk_url`` or ``slug_url``.

    .. code-block:: python

        @pk_url(MyModel)
        @record_view
        def view(request, instance):
            # ...
    """
    @wraps(function)
    def wrapper(request, instance, *args, **kwargs):
        ip_address = request.META["REMOTE_ADDR"]
        View(content_object=instance, ip_address=ip_address).save()
        return function(request, instance, *args, **kwargs)

    return wrapper
