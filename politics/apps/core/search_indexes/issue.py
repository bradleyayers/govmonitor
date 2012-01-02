# coding=utf-8
from ..models import Issue
from haystack import site
from haystack.indexes import *


class IssueIndex(RealTimeSearchIndex):
    """The :class:`Issue` search index."""

    text = CharField(document=True, use_template=True)


site.register(Issue, IssueIndex)
