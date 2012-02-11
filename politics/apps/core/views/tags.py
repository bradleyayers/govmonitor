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
    tags = Tag.objects.annotate(issue_count=Count("issue"))
    tags = tags.filter(issue_count__gt=0).order_by("-issue_count")
    page = Paginator(tags, 32).page(request.GET.get("page", 1))

    # Split the tags into rows of length 4.
    indices = range(0, len(page.object_list), 4)
    tag_rows = [page.object_list[i:i+4] for i in indices]

    return {"page": page, "tag_rows": tag_rows}


@slug_url(Tag)
@render_to_template("core/tags/show.html")
def show(request, tag):
    """Shows information about a tag."""
    issues = Issue.objects.filter(tags=tag).order_by("name")
    page = Paginator(issues, 25).page(request.GET.get("page", 1))
    return {"page": page, "tag": tag}
