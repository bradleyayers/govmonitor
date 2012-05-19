# coding=utf-8
def group_n(iterable, n):
    """Collects the items in an iterable into groups of size ``n``.

    .. code-block:: python

        >>> group_n([1, 2, 3, 4, 5, 6, 7], 2)
        [[1, 2], [3, 4], [5, 6], [7]]

    :param iterable: The items to group.
    :type  iterable: ``iterable``
    :param        n: The group size.
    :type         n: ``int``
    """
    return (iterable[i:i + n] for i in xrange(0, len(iterable), n))
