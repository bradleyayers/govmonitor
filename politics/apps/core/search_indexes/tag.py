# coding=utf-8
from ..models import Tag
from haystack import site
from haystack.indexes import *


class TagIndex(RealTimeSearchIndex):
    """The :class:`Tag` search index."""

    text = CharField(document=True, use_template=True)


site.register(Tag, TagIndex)
