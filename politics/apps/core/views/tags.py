# coding=utf-8
from django.db.models import Avg, Count
from politics.apps.core.models import Issue, Tag
from politics.utils import group_n
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
    page = Paginator(tags, 27).page(request.GET.get("page", 1))

    return {
        "average_issues": int(round(tags.aggregate(avg=Avg("issue_count"))["avg"])),
        "page": page,
        "tag_rows": group_n(tags, 3),
        "tags": tags,
    }


@slug_url(Tag)
@render_to_template("core/tags/show.html")
def show(request, tag):
    """Shows information about a tag."""
    issues = Issue.objects.filter(tags=tag).order_by("name")
    page = Paginator(issues, 25).page(request.GET.get("page", 1))

    # Retrieve the tags that occur most frequently with this one.
    related_tags = Issue.common_tags(tag.issue_set.all())
    related_tags.remove(tag)

    return {"page": page, "related_tags": related_tags, "tag": tag}
