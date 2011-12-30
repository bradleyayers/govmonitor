# coding=utf-8
from haystack.query import SearchQuerySet
from politics.apps.core.models import Tag
from politics.utils.decorators import render_json


@render_json
def tags(request):
    """Returns the names of tags matching the given query as JSON.

    Used for autocompletion in tag inputs.
    """
    query = request.GET.get("q", "*")
    results = SearchQuerySet().models(Tag).filter(content=query)
    return [result.name for result in results]
