# coding=utf-8
from django.http import HttpResponse
from haystack.query import SearchQuerySet, SQ
from politics.apps.core.models import Tag
from politics.utils.decorators import render_json
from pyquery import PyQuery
import requests


def _get_html_title(url):
    """Attempts to retrieve the HTML title of a URL.

    This only works if the URL responds to HTTP requests, in which case the
    contents of its ``title`` element will be returned; otherwise ``None``.

    :param url: The URL of the page.
    :type  url: ``str``
    :returns: The URL's title or ``None``.
    :rtype: ``str`` or ``None``
    """
    blacklist = (
        "::1",
        "127.0.0.1",
        "localhost",
        "ip6-loopback",
        "ip6-localhost",
    )

    for host in blacklist:
        if url.find(host) > -1:
            return None

    try:
        response = requests.get(url, timeout=10)
        selector = PyQuery(response.content)
        return selector("title")[0].text.strip()
    except:
        return None


@render_json
def tags(request):
    """Returns the names of tags matching the given query as JSON.

    Used for autocompletion in tag inputs.
    """
    # Escape the query.
    query = request.GET.get("q", "*")
    query = SearchQuerySet().query.clean(query)

    if query == "":
        return []

    # Retrieve tags that match an autocomplete (ngram) search or a normal
    # search so derivative words match (e.g. "immigrants" => "immigration").
    results = SearchQuerySet().models(Tag).load_all()
    results = results.filter(SQ(content=query) | SQ(name_autocomplete=query))

    return [result.object.name for result in results]


@render_json
def title(request):
    """Attempts to retrieve the title of a URL."""
    if request.method != "GET":
        return HttpResponse(status=405)

    if "url" not in request.GET:
        return HttpResponse(status=400)

    return _get_html_title(request.GET["url"])
