# coding=utf-8
from ..models import Tag
from haystack import site
from haystack.indexes import *


class TagIndex(RealTimeSearchIndex):
    """The :class:`Tag` search index."""

    text = CharField(document=True, use_template=True)
    name_autocomplete = EdgeNgramField(model_attr="name")


site.register(Tag, TagIndex)
