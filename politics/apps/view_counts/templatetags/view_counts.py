# coding=utf-8
from ..models import View
from django import template
from django.db.models import Count


register = template.Library()


@register.filter
def view_count(instance):
    """Returns the view count of the given object.

    :param instance: The object whose view count is to be returned.
    :type  instance: ``django.db.models.Model``
    :returns: The view count of ``instance``.
    :rtype: ``int``
    """
    views = View.objects.get_for_model(instance)
    return views.values("ip_address").annotate(Count("ip_address")).count()
