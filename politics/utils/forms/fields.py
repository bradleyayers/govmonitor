# coding=utf-8
from .widgets import ReCAPTCHAWidget
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from recaptcha.client import captcha


class ReCAPTCHAField(forms.Field):
    """A field that renders and validates a reCAPTCHA dialogue.

    As reCAPTCHA requires the user's IP address, forms that use this field
    must override ``__init__`` to take a request object. For example:

        from django import forms
        from politics.utils.fields import ReCAPTCHAField


        class MyForm(forms.Form):
            def __init__(request, *args, **kwargs):
                super(MyForm, self).__init__(*args, **kwargs)
                self.fields["captcha"] = ReCAPTCHAField(request)

    reCAPTCHA public/private keys are retrieved from ``django.conf.settings``
    (``RECAPTCHA_PUBLIC_KEY`` and ``RECAPTCHA_PRIVATE_KEY``, respectively).
    """

    _ERROR_MESSAGES = {
        "INCORRECT": "Incorrect, try again.",
    }

    def __init__(self, request, *args, **kwargs):
        self._request = request
        kwargs["widget"] = ReCAPTCHAWidget()
        super(ReCAPTCHAField, self).__init__(*args, **kwargs)

    def clean(self, value):
        response = captcha.submit(value[0], value[1],
                                  settings.RECAPTCHA_PRIVATE_KEY,
                                  self._request.META["REMOTE_ADDR"])

        if not response.is_valid:
            raise ValidationError(self._ERROR_MESSAGES["INCORRECT"])

        return value
