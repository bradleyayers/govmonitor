# coding=utf-8


# Constant time intervals: those whose durations (essentially) never change.
# These should be in ascending order of duration (expressed in seconds).
_INTERVALS = (
    (1, "second"),
    (60, "minute"),
    (3600, "hour"),
    (86400, "day"),
    (604800, "week"),
)


def interval_string(a, b):
    """Returns a string representing the interval between two points in time.

    :param a: The first point in time.
    :type  a: ``datetime.datetime``
    :param b: The second point in time.
    :type  b: ``datetime.datetime``

    :returns: A string representing the interval between ``a`` and ``b``.
    :rtype: ``str``
    """
    a, b = sorted([a, b])
    difference = (b - a).total_seconds()

    # The first interval is our greatest accuracy. By skipping it, any smaller
    # differences will be "rounded up" and expressed in terms of that interval.
    for i, interval in enumerate(_INTERVALS[1:], start=1):
        # The difference can't be meaningfully expressed in terms of this
        # interval (it's too small), so we'll use the previous one.
        if difference < interval[0]:
            value = difference // _INTERVALS[i - 1][0]
            return "%d %s%s" % (value, _INTERVALS[i - 1][1], _pluralize(value))

    years = _get_years_between(a, b)
    if years > 0:
        return "%d year%s" % (years, _pluralize(years))

    months = _get_months_between(a, b)
    if months > 0:
        return "%d month%s" % (months, _pluralize(months))

    weeks = difference // _INTERVALS[-1][0]
    return "%d week%s" % (weeks, _pluralize(weeks))


def _get_months_between(a, b):
    """Calculates and returns the number of months between two points in time.

    A month is said to have passed from one point in time when we arrive at the
    same point in the following month, e.g. 01/01/2011 to 01/02/2011.

    .. note::

        Assumes that ``b`` follows ``a``.

    :param a: The first point in time.
    :type  a: ``datetime.datetime``
    :param b: The second point in time.
    :type  b: ``datetime.datetime``

    :returns: The number of months between ``a`` and ``b``.
    :rtype: ``int``
    """
    # Different months doesn't mean there's a month between them, e.g. there's
    # only a day between 31/01/2011 and 01/02/2011. Check if it falls short.
    short = b.day < a.day
    short |= b.day == a.day and b.time() < a.time()

    # The dates' years may be different, making month calculations meaningless.
    # By adding 12 months to b for each year different, we bring them into the
    # same "domain" so their difference can be calculated. For example, for
    # 01/2012 and 12/2011, the former becomes 13/2011; 13 - 12 is 1 month.
    year_difference = b.year - a.year
    return (b.month + 12 * year_difference) - a.month - int(short)


def _pluralize(number, suffix="s"):
    """Returns the plural suffix (if any) that should be used for a number.

    :param number: The number.
    :type  number: ``int``
    :param suffix: The suffix.
    :type  suffix: ``str``

    :returns: An empty string if ``number`` is 1, otherwise ``suffix``.
    :rtype: ``str``
    """
    return "" if number == 1 else suffix


def _get_years_between(a, b):
    """Calculates and returns the number of years between two points in time.

    A year is said to have passed from one point in time when we arrive at the
    same point in the following year, e.g. from 01/01/2011 to 01/01/2012. For
    leap years, a year is said to have passed from the 29th of February on the
    1st of March the following year.

    .. note::

        Assumes that ``b`` follows ``a``.

    :param a: The first point in time.
    :type  a: ``datetime.datetime``
    :param b: The second point in time.
    :type  b: ``datetime.datetime``

    :returns: The number of years between ``a`` and ``b``.
    :rtype: ``int``
    """
    # Different years doesn't mean there's a year between them, e.g. there's
    # only a day between 31/12/2011 and 01/01/2012. Check if it falls short.
    short = b.month < a.month
    short |= b.month == a.month and b.day < a.day
    short |= b.month == a.month and b.day == a.day and b.time() < a.time()

    return b.year - a.year - int(short)
