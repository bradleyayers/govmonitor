# coding=utf-8
from django import template
from politics.apps.votes.models import Vote


register = template.Library()


@register.inclusion_tag("votes/vote_data.html", takes_context=True)
def vote_data(context, models):
    """Renders the ``AP.Votes.VoteData`` JavaScript variable to the page.

    .. note::

        Assumes that all the given models are of the same type.

    :param context: The template context.
    :type  context: ``django.template.base.context.Context``
    :param  models: The models whose vote data is to be retrieved.
    :type   models: *Iterable* of ``django.db.models.Model``
    """
    data = {}
    user = context["request"].user

    if user.is_authenticated():
        votes = Vote.objects.get_for_model(models[0])
        votes = votes.filter(author=user, object_id__in=(m.pk for m in models))
        data = dict((vote.object_id, vote.type) for vote in votes)

    return {"data": data}
