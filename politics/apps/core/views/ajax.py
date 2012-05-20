# coding=utf-8
from haystack.query import SearchQuerySet, SQ
from politics.apps.core.models import Tag
from politics.utils.decorators import render_json


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
