# coding=utf-8
from django.db import models
from politics.utils.feature_markdown import Markdown


class MarkdownField(models.TextField):
    """Stores markdown, converted to HTML and stored in another field on save.

    By default, the resulting HTML is stored in the field whose name is given
    by appending "_html" to this field's name. This can be changed by passing
    an ``html_field_name`` argument to the field's constructor.

    The markdown is converted to HTML on every save unless the constructor's
    ``on_change`` argument is ``True``. This causes a database query to be
    performed on save to determine if any changes have been made.

    With ``politics.utils.feature_markdown`` used to perform the conversion,
    certain markdown features (e.g. images) can be enabled or disabled using
    the keyword arguments of the same name. To disable images, for example:

    .. code-block:: python

        description = MarkdownField(disable=["images"])
        description_html = models.TextField()

    :param         disable: Markdown features that are to be disabled.
    :type          disable: *Iterable* or ``None``
    :param          enable: Markdown features that are to be enabled.
    :type           enable: *Iterable* or ``None``
    :param html_field_name: The name of the field in which the HTML will be
                            stored. If ``None``, this field's name plus "_html".
    :type  html_field_name: ``None`` or ``str``
    :param       on_change: If ``True``, the conversion will only be performed
                            if changes are detected. Requires a database query.
    :type        on_change: ``bool``
    """

    def __init__(self, disable=None, enable=None, html_field_name=None,
                 on_change=False, *args, **kwargs):
        self._html_field_name = html_field_name
        self._markdown = Markdown(disable=disable, enable=enable)
        self._on_change = on_change

        super(MarkdownField, self).__init__(*args, **kwargs)

    def contribute_to_class(self, cls, name):
        # Determine the HTML field's name.
        if getattr(self, "_html_field_name", None) is None:
            self._html_field_name = "{0}_html".format(name)

        super(MarkdownField, self).contribute_to_class(cls, name)

    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname)

        # We can't detect changes if the model instance is new.
        if self._on_change and not add:
            model = model_instance.__class__
            old_model_instance = model.objects.get(pk=model_instance.pk)

            # If the value hasn't changed, don't perform the conversion.
            if value == getattr(old_model_instance, self.attname):
                return value

        # Convert the markdown to HTML, store it.
        result = self._markdown.convert(value)
        setattr(model_instance, self._html_field_name, result)

        return value


# Add south introspection rules.
try:
    from south.modelsinspector import add_introspection_rules
    pattern = "^politics\.utils\.models\.fields\.MarkdownField$"
    add_introspection_rules([], [pattern])
except ImportError:
    pass
