# coding=utf-8
# We don't need to import the SearchIndex subclasses as the submodules register
# themselves with haystack.site; it's enough to just import the submodules.
from . import issue, tag
