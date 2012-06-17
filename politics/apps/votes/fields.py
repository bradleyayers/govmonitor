# coding=utf-8
from django.db import models


class ScoreField(models.FloatField):
    """Used to cache a model's vote score.

    Effectively acts as a marker for :class:`Vote`. Add an instance of this
    field to a model and it will automagically be updated as votes are cast.

    .. code-block:: python

        from django.db import models
        from politics.apps.votes.fields import ScoreField


        class MyModel(models.Model):
            score = ScoreField()

    The following demonstrates automatic updating of the field:

    .. code-block:: python

        >>> from django.contrib.auth.models import User
        >>> from politics.apps.votes.models import Vote
        >>> model = MyModel.objects.get(...)
        >>> model.score
        0
        >>> Vote(author=..., content_object=model, type=Vote.UP).save()
        >>> model = MyModel.objects.get(pk=model.pk)
        >>> model.score
        0.2686
    """

    # Override to provide a default default.
    def __init__(self, default=0, *args, **kwargs):
        super(ScoreField, self).__init__(default=default, *args, **kwargs)


# Add South introspection rules.
try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^politics\.apps\.votes\.fields\.ScoreField"])
except ImportError:
    pass
