# coding=utf-8
from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe
from recaptcha.client import captcha


class ReCAPTCHAWidget(forms.widgets.Widget):
    """A widget that displays a reCAPTCHA dialogue."""

    _CHALLENGE_FIELD_NAME = "recaptcha_challenge_field"
    _RESPONSE_FIELD_NAME = "recaptcha_response_field"

    def render(self, name, value, attrs=None):
        # TODO: Should we use SSL?
        return mark_safe(captcha.displayhtml(settings.RECAPTCHA_PUBLIC_KEY))

    def value_from_datadict(self, data, files, name):
        return [data.get(self._CHALLENGE_FIELD_NAME, None),
                data.get(self._RESPONSE_FIELD_NAME, None)]
