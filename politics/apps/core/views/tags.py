# coding=utf-8
from ..models import Issue, Tag
from django.db.models import Count
from politics.utils.decorators import render_to_template, slug_url
from politics.utils.paginator import Paginator


@render_to_template("core/tags/list.html")
def list(request):
    """Displays a paginated list of tags.

    The tags are displayed in descending order of popularity. A tag's
    popularity is the number of issues that have been assigned to it.
    """
    tags = Tag.objects.annotate(Count("issue")).order_by("-issue__count")
    page = Paginator(tags, 32).page(request.GET.get("page", 1))

    # Split the tags into groups of 4 to be displayed as rows in the table.
    tag_groups = [page.object_list[i:i+4] for i in range(0, len(tags), 4)]
    return {"page": page, "tag_groups": tag_groups}


@slug_url(Tag)
@render_to_template("core/tags/show.html")
def show(request, tag):
    """Shows information about a tag."""
    issues = Issue.objects.filter(tags=tag).order_by("name")
    page = Paginator(issues, 25).page(request.GET.get("page", 1))
    return {"page": page, "tag": tag}
