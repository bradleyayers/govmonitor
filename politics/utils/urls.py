# coding=utf-8
from django.conf.urls.defaults import patterns
import re


def prefix(prefix, patterns):
    """Prefix the regular expressions of a list of URL patterns.

    The following lists are equivalent:

    .. code-block:: python

        urlpatterns = patterns("",
            url(r"^(?P<pk>\d+)/$", show),
            url(r"^(?P<pk>\d+)/edit/$", edit)
        ) 

        prefixed_urlpatterns = prefix("^(?P<pk>\d+)/", patterns("",
            url(r"$", show),
            url(r"edit/$", edit)
        ))

    This method is particularly helpful in dealing with Django's inability to
    capture URL parameters when using namespaces. Just prefix the patterns!

    :param   prefix: The string to be prefixed to all regular expressions.
    :type    prefix: ``str``
    :param patterns: The URL patterns that are to be prefixed.
    :type  patterns: *Iterable*
    """
    for pattern in patterns:
        pattern.regex = re.compile(prefix + pattern.regex.pattern, re.UNICODE)

    return patterns