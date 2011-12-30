# coding=utf-8
from django.core.paginator import Paginator as BasePaginator


class Paginator(BasePaginator):
    """A paginator that handles invalid page numbers."""

    def page(self, number):
        """Returns a ``Page`` object for the given 1-based page number.

        ``number`` is first converted to an ``int`` and is then truncated to
        the range of valid page numbers. If it can't be converted, it defaults
        to 1. If it's less than 1, it is rounded up to 1, if it's greater than
        the maximum page number ``n``, it is rounded down to ``n``.

        :param number: The 1-based page number.
        :type  number: ``int`` or ``str``
        """
        try:
            number = max(1, min(self.num_pages, int(number)))
        except ValueError:
            number = 1

        return super(Paginator, self).page(number)
