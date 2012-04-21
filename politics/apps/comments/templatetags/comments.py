# coding=utf-8
from django import template
from politics.apps.comments.models import Comment


register = template.Library()


@register.inclusion_tag("comments/_comments.html")
def comments(instance):
    """Render comments that have been made on an object.

    :param instance: The object whose comments are to be rendered.
    :type  instance: ``django.db.models.Model``
    """
    comments = Comment.objects.get_for_instance(instance).order_by("created_at")
    return {"comments": comments}
