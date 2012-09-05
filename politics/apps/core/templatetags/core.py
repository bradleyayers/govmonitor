# coding=utf-8
from django import template
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.template import Node, TemplateSyntaxError
from politics.apps.core.models import View
from politics.utils import group_n as base_group_n


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


class AbsoluteURLNode(Node):
    """The node used in the ``absolute_url`` tag."""

    def __init__(self, name, args):
        """
        :param name: The view name.
        :type  name: ``str``
        :param args: Arguments required to resolve the URL.
        :type  args: *Iterable*
        """
        super(AbsoluteURLNode, self).__init__()
        self.name = name
        self.args = args

    def render(self, context):
        site = Site.objects.get_current()
        args = [arg.resolve(context) for arg in self.args]
        return "http://%s%s" % (site.domain, reverse(self.name, args=args))


@register.tag
def absolute_url(parser, token):
    """Similar to the built-in URL tag, but returns an absolute URL.

    Uses the domain of the current site.
    """
    bits = token.split_contents()
    name = bits.pop(0)

    if len(bits) < 1:
        raise TemplateSyntaxError("Malformed arguments to %s tag." % name)

    name = bits.pop(0)
    args = [parser.compile_filter(bit) for bit in bits]
    return AbsoluteURLNode(name, args)


@register.simple_tag(takes_context=True)
def comma(context):
    """Prints a comma after all but the last item in a for loop."""
    is_last = context["forloop"]["last"]
    return "," if not is_last else ""


@register.inclusion_tag("core/elections/_summary.html")
def election_summary(election):
    """Renders a summary of an election.

    :param election: The election.
    :type  election: ``politics.apps.core.models.Election``
    """
    return {
        "election": election,
        "parties": election.parties.all()
    }


@register.filter
def get(dictionary, key):
    """Retrieve a value from a dictionary using the given key.

    :param dictionary: The dictionary.
    :type  dictionary: ``dict``
    :param        key: The key.
    :type         key: ``str``
    """
    return dictionary[key]


@register.filter
def group_n(iterable, n):
    """Collects the items in an iterable into groups of size ``n``.

    :param iterable: The items to group.
    :type  iterable: *Iterable*
    :param        n: The group size.
    :type         n: ``int``
    """
    return base_group_n(iterable, n)


@register.filter
def indent(value, amount):
    """Indent each line of the given text by some number of spaces.

    :param  value: The text to indent.
    :type   value: ``str``
    :param amount: The number of spaces to indent by.
    :type  amount: ``int``
    """
    return "\n".join(" " * amount + line for line in value.split("\n"))


@register.filter
def interval_string(value, reference=None):
    """Returns a string representing the interval between two points in time.

    If ``reference`` is ``None``, ``date.today()`` or ``datetime.now()`` will be
    used depending on the type of ``value``.

    :param     value: The first point in time.
    :type      value: ``datetime.date`` or ``datetime.datetime``
    :param reference: The second point in time or ``None``.
    :type  reference: ``datetime.date``, ``datetime.datetime``, or ``None``
    :returns: A string representing the interval between ``value`` and either
              ``reference`` or ``datetime.now()``.
    :rtype: ``str``
    """
    from datetime import date, datetime
    from politics.utils import timestring

    if reference is None:
        reference = datetime.now() if isinstance(value, datetime) else date.today()

    return timestring.interval_string(value, reference)


@register.inclusion_tag("core/issues/_summary.html")
def issue_summary(issue):
    """Renders a summary of an issue suitable for display in a list of issues.

    :param issue: The issue.
    :type  issue: :class:`Issue`
    """
    views = View.objects.exclude(stance=View.UNKNOWN).filter(issue=issue)
    views = views.order_by("party__name").select_related("party")
    return {"issue": issue, "views": views}


@register.filter
def json(value):
    """Converts the given value to JSON.

    .. note::

        Doesn't escape the resulting string.

    :param value: The value that is to be converted to JSON.
    :returns: ``value`` as JSON.
    :rtype: ``str``
    """
    import json

    return json.dumps(value)


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
    minimum = max(page.number - near, 1)
    maximum = min(minimum + near * 2, page.paginator.num_pages)
    minimum = max(maximum - near * 2, 1)

    return {
        "current_page": page,
        "pages": range(minimum, maximum + 1),
        "request": context["request"],
    }


@register.inclusion_tag("core/parties/_summary.html")
def party_summary(party):
    """Renders a summary of a party suitable for display in a list of parties.

    :param party: The party.
    :type  party: :class:`Party`
    """
    return {"party": party}


@register.filter
def percentage(value, precision=0):
    """Returns the given value as a percentage.

    .. code-block::

        >>> percentage(0.1337)
        '13%'
        >>> percentage(42.42, 1)
        '42.4%'

    :param     value: The value.
    :type      value: ``float``
    :param precision: Round to this many decimal places.
    :type  precision: ``int``
    """
    if 0 <= value <= 1:
        value *= 100

    return ("%." + str(precision) + "f%%") % value


@register.simple_tag
def stance_icon(stance):
    return {
        View.OPPOSE: "icon-thumbs-down",
        View.SUPPORT: "icon-thumbs-up",
        View.UNCLEAR: "icon-question-sign",
    }.get(stance, "")


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

    bits = token.split_contents()
    name = bits.pop(0)

    try:
        return QueryStringNode(_parse_token_kwargs(bits, parser))
    finally:
        # If bits isn't empty, the arguments couldn't be parsed.
        if bits:
            raise TemplateSyntaxError("Malformed arguments to %s tag." % name)


class SquashSpacesNode(Node):
    """The node used in the ``squashspaces`` tag."""

    def __init__(self, nodelist):
        super(SquashSpacesNode, self).__init__()
        self.nodelist = nodelist

    def render(self, context):
        import re

        output = self.nodelist.render(context)
        return re.sub("\s+", " ", output)


@register.tag
def squashspaces(parser, token):
    """Squashes multiple spaces into a single space.

    .. code-block:: django

        {% squashspaces %}
            <a>  <b>  Hello    world!  </b>  </a>
        {% endsquashspaces %}

    .. code-block:: django

        <a> </b> Hello world! </b> </a>
    """
    nodelist = parser.parse(("endsquashspaces",))
    parser.delete_first_token()
    return SquashSpacesNode(nodelist)


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


@register.simple_tag
def view_url(issue_or_view, party=None):
    """Returns the path to a view.

    This function can be called in two ways: the view itself can be given, or an
    issue and a party (the corresponding view will be linked to). For example:

    .. code-block:: django

        {% view_url view %}
        {% view_url issue party %}

    :param issue_or_view: An issue or the view to link to.
    :type  issue_or_view: ``politics.apps.core.models.Issue`` or
                          ``politics.apps.core.models.View``
    :param         party: A party or ``None``.
    :type          party: ``politics.apps.core.models.Party`` or ``None``
    """
    issue = issue_or_view
    if isinstance(issue_or_view, View):
        party = issue.party
        issue = issue.issue

    return reverse("core:issues:view", kwargs={
        "issue_pk": issue.pk,
        "issue_slug": issue.slug,
        "party_pk": party.pk,
        "party_slug": party.slug
    })