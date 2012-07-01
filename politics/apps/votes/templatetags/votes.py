# coding=utf-8
from collections import Iterable
from django import template
from django.template import Node, TemplateSyntaxError
from django.template.loader import render_to_string
from politics.apps.votes.models import Vote


register = template.Library()


class VoteDataNode(Node):
    """The node used in the ``vote_data`` tag."""

    def __init__(self, variables):
        self.variables = [template.Variable(v) for v in variables]

    def render(self, context):
        data = {}
        user = context["request"].user

        if user.is_authenticated():
            # Resolve the variables and flatten the list.
            models = []
            for v in self.variables:
                v = v.resolve(context)
                models += v if isinstance(v, Iterable) else [v]

            if len(models) > 0:
                pks = (model.pk for model in models)
                votes = Vote.objects.get_for_model(models[0])
                votes = votes.filter(author=user, object_id__in=pks)
                data = dict((vote.object_id, vote.type) for vote in votes)

        return render_to_string("votes/vote_data.html", {"data": data})


@register.tag
def vote_data(parser, token):
    """Renders the ``AP.Votes.VoteData`` JavaScript variable to the page.

    Takes one or more arguments, each either a model or an iterable of models.
    If the user isn't authenticated or hasn't voted, the object will be empty.

    .. code-block:: html

        <script type="text/javascript">
        AP.Votes.VoteData = {1: "up", 2: "down", ...};
        </script>

    .. note::

        Assumes that the models are all of the same type.
    """
    bits = token.split_contents()
    name = bits.pop(0)

    if len(bits) == 0:
        raise TemplateSyntaxError("%s requires at least one argment." % name)

    return VoteDataNode(bits)
