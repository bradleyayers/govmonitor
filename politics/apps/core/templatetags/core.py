# coding=utf-8
from __builtin__ import max as builtin_max
from django import template
from django.core.urlresolvers import reverse
from django.template import Node


register = template.Library()


def _parse_token_kwargs(bits, parser):
    """A utility method for parsing token keyword arguments.

    This method is used to add keyword argument support to template tags,
    allowing them to handle syntax like: ``{% example_tag a=0 b="c" %}``.
    Simply provide the split contents of the tag's token and a parser:

    .. code-block:: python

        @register.tag
        def example_tag(parser, token):
            bits = token.split_contents()[1:]
            kwargs = _parse_token_kwargs(bits, parser)
            # ...

    The arguments are parsed into a dictionary where the values are
    ``FilterExpression`` objects which can then be resolved in a template
    context. A node's ``render`` method, would thus look something like this:

    .. code-block:: python

        def render(self, context):
            # Assuming kwargs holds the arguments.
            for key, value in self.kwargs.iteritems():
                value = value.resolve(context)
                # ...

    .. warning::

        Positional arguments aren't currently supported.
    """
    import re

    if not bits:
        return {}

    kwargs = {}
    expression = re.compile(r"(\w+)=(.+)")

    while bits:
        match = expression.match(bits[0])

        if not match:
            return kwargs

        del bits[0]
        key, value = match.groups()
        kwargs[key] = parser.compile_filter(value)

    return kwargs


@register.filter
def getattr_iterable(iterable, name):
    """Calls ``getattr`` on each item in an iterable and returns the results.

    .. code-block:: python

        >>> models = Model.objects.all()
        >>> getattr_iterable(models, "pk")
        [1, 2, 3, ...]

    :param iterable: The items.
    :type  iterable: ``Iterable``
    :param     name: The name of the attribute to be retrieved.
    :type      name: ``str``
    """
    return [getattr(item, name) for item in iterable]


@register.filter
def interval_string(value, reference=None):
    """Returns a string representing the interval between two points in time.

    If ``reference`` is ``None``, ``datetime.now()`` is used.

    :param     value: The first point in time.
    :type      value: ``datetime.datetime``
    :param reference: The second point in time or ``None``.
    :type  reference: ``datetime.datetime`` or ``None``

    :returns: A string representing the interval between ``value`` and either
              ``reference`` or ``datetime.now()``.
    :rtype: ``str``
    """
    from datetime import datetime
    from politics.utils import timestring

    return timestring.interval_string(value, reference or datetime.now())


@register.inclusion_tag("core/issues/_summary.html")
def issue_summary(issue):
    """Renders a summary of an issue suitable for display in a list of issues.

    :param issue: The issue.
    :type  issue: :class:`Issue`
    """
    from politics.apps.core.models import View

    views = View.objects.exclude(stance=View.UNKNOWN).filter(issue=issue)
    views = views.order_by("party__name").select_related("party")
    return {"issue": issue, "views": views}


@register.simple_tag(takes_context=True)
def login_link(context, text):
    """Returns a link to the login view.

    Sets the ``next`` querystring parameter to the current path so the user is
    returned to the page containing the link after they've logged in. So if the
    user was on the page ``/models/1`` for example, this::

        {% login_link "Log in" %}

    would be rendered as this::

        <a href="/login?next=/models/1">Log in</a>

    :param context: The context in which the link should be rendered.
    :type  context: ``django.template.base.context.Context``
    :param    text: The link text.
    :type     text: ``str``

    :returns: A HTML link to the login view that redirects to the current
              page, with text ``text``.
    :rtype: ``str``
    """
    return "<a href=\"%s?next=%s\">%s</a>" % (reverse("core:login"),
                                              context["request"].path, text)


@register.filter
def max(values):
    """Returns the maximum item in an iterable.

    :param values: The items.
    :type  values: ``Iterable``
    """
    return builtin_max(values)


@register.simple_tag
def tag_link(tag):
    """Renders a link to a tag.

    :param tag: The tag to link to.
    :type  tag: :class:`Tag`
    :returns: An HTML link to ``tag``.
    :rtype: ``str``
    """
    return "<a class=\"tag\" href=\"{0}\">{1}</a>".format(
        reverse("core:tags:show", kwargs={"pk": tag.pk, "slug": tag.slug}),
        tag.name
    )


@register.simple_tag
def user_link(user, text=None):
    """Renders a link to a user's profile.

    The link text defaults to the user's full name. For example, if the context
    variable ``user`` refers to a user with ID 1 and name "Chris Doble", this::

        {% user_link user %}
        {% user_link user "Chris Doble's Profile" %}

    would be rendered as this::

        <a href="/users/1">Chris Doble</a>
        <a href="/users/1">Chris Doble's Profile</a>

    :param user: The user whose profile will be linked to.
    :type user: ``django.contrib.auth.models.User``
    :param text: The link text to display. Defaults to the user's full name.
    :type text: ``None`` or ``str``
    :returns: An HTML link to ``user``'s profile.
    :rtype: ``str``
    """
    path = reverse("core:users:show", args=[user.pk])
    return "<a href=\"%s\">%s</a>" % (path, text or user.get_full_name())


@register.inclusion_tag("core/_page_links.html", takes_context=True)
def page_links(context, page, near=2):
    """Renders links to pages of paginated content.

    Links to a number of pages near the current page and to the first and last
    pages if they aren't near. If we were on page 10 and ``near`` was 2, for
    example, pages 1, 8, 9, 10, 11, 12, and n would be linked to.

    :param context: The context in which the tag was used.
    :type  context: ``dict``
    :param    page: The current page.
    :type     page: ``django.core.paginator.Page``
    :param    near: The number of pages that should be linked to before and
                    after the current page (if that many pages are available).
    :type     near: ``int``

    .. note::

        The current request must be available in the context as "request"; this
        will happen if ``django.core.context_processors.request`` is enabled.
    """
    # Calculate the range of near pages.
    minimum = builtin_max(page.number - near, 1)
    maximum = min(minimum + near * 2, page.paginator.num_pages)
    minimum = builtin_max(maximum - near * 2, 1)

    return {
        "current_page": page,
        "pages": range(minimum, maximum + 1),
        "request": context["request"],
    }


class QueryStringNode(Node):
    """The node used in the ``query_string`` tag."""

    def __init__(self, kwargs):
        super(QueryStringNode, self).__init__()
        self.kwargs = kwargs

    def render(self, context):
        from urllib import urlencode

        kwargs = dict(context["request"].GET)
        for key, value in self.kwargs.iteritems():
            if key not in ("", None):
                # value is a FilterExpression object.
                kwargs[key] = value.resolve(context)

        return "?" + urlencode(kwargs, doseq=True)


@register.tag
def query_string(parser, token):
    """Constructs a query string given keyword arguments.

    The current query string is used as a base; its values are carried through
    if they're not overridden. Starting with "?age=21&name=Chris", for example:

    .. code-block:: django

        {% query_string location=Australia name="Chris Doble" %}
        ?age=21&location=Australia&name=Chris+Doble

    .. note::

        The current request must be available in the context as "request"; this
        will happen if ``django.core.context_processors.request`` is enabled.
    """
    from django.template import TemplateSyntaxError

    bits = token.split_contents()
    name = bits.pop(0)

    try:
        return QueryStringNode(_parse_token_kwargs(bits, parser))
    finally:
        # If bits isn't empty, the arguments couldn't be parsed.
        if bits:
            raise TemplateSyntaxError("Malformed arguments to %s tag." % name)
