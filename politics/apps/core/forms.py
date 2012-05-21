# coding=utf-8
from .models import Issue, Party, Reference, Tag, View
from django import forms
from django.contrib import auth
from django.contrib.auth.models import User
from django.core import validators
from django.core.exceptions import ValidationError
from django.template.defaultfilters import slugify
from politics.utils.forms import ReCAPTCHAField


class TagsField(forms.Field):
    """A form field for specifying :class:`Tag`s.

    Takes a string of space-separated tag names, returns a list of
    :class:`Tag`s with matching names (creates new ones if necessary).
    """

    default_error_messages = {
        "tag_length": "{0} exceeds the maximum tag length of {1} characters."
    }

    def __init__(self, *args, **kwargs):
        if "widget" not in kwargs:
            kwargs["widget"] = forms.TextInput

        super(TagsField, self).__init__(*args, **kwargs)

    def prepare_value(self, value):
        if isinstance(value, list):
            # Convert the list of tag primary keys to human-readble text.
            value = " ".join([Tag.objects.get(pk=pk).name for pk in value])

        return value

    def to_python(self, value):
        if value in validators.EMPTY_VALUES:
            return []

        # Extract non-empty tag names, slugify them.
        names = [slugify(name) for name in value.split(" ") if name]

        # Ensure that no name exceeds the maximum length.
        max_length = Tag._meta.get_field("name").max_length
        long_names = [name for name in names if len(name) > max_length]

        if long_names:
            message = self.error_messages["tag_length"]
            message = [message.format(name, max_length) for name in long_names]
            raise ValidationError(message)

        # Fetch the tags. If a tag doesn't exist, return an unsaved instance.
        # We can't use get_or_create because we don't actually want to create.
        tags = []
        for name in names:
            try:
                tags.append(Tag.objects.get(name=name))
            except Tag.DoesNotExist:
                tags.append(Tag(name=name))

        return tags


class IssueForm(forms.ModelForm):
    """A form for creating ``Issue``s."""

    tags = TagsField(widget=forms.TextInput(attrs={
        "placeholder": "e.g. education, international-relations"
    }))

    description = forms.CharField(widget=forms.Textarea(attrs={
        "placeholder": "A description of the issue."
    }))

    class Meta:
        model = Issue
        fields = ("description", "name", "tags")

    def clean(self):
        # The name cannot be "edit" as that conflicts with the edit URL.
        # TODO: Remove this constraint, possibly by having a base class?
        name = self.cleaned_data.get("name")
        if name and slugify(name) == "edit":
            self._errors["name"] = self.error_class(["Invalid name."])
            del self.cleaned_data["name"]

        return self.cleaned_data

    def save(self, *args, **kwargs):
        # Save any tags that were created by the TagsField.
        [tag.save() for tag in self.cleaned_data["tags"] if tag.pk is None]
        return super(IssueForm, self).save(*args, **kwargs)


class LoginForm(forms.Form):
    """A login form."""

    _ERROR_MESSAGES = {
        "INVALID_CREDENTIALS": "Incorrect, try again.",
    }

    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self._user = None

    def clean(self):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")
        self._user = auth.authenticate(username=email, password=password)

        if email and password and not self._user:
            raise ValidationError(self._ERROR_MESSAGES["INVALID_CREDENTIALS"])

        return self.cleaned_data

    def login(self, request):
        """Logs the user in. To be called when we know the form is valid."""
        if not self._user:
            raise Exception("_user has not been set.")

        auth.login(request, self._user)


class PartyForm(forms.ModelForm):
    """A form for creating/editing :class:`Party` objects."""

    class Meta:
        model = Party
        exclude = ("slug",)


class ReferenceForm(forms.ModelForm):
    """A form for creating :class:`Reference`s.

    A :class:`Reference` with a ``view`` must be passed to the form! This is
    required so we can determine if a URL has already been submitted. Example:

    .. code-block:: python

        >>> form = ReferenceForm(instance=Reference(view=view))
    """

    _ERROR_MESSAGES = {
        "DUPLICATE_URL": "This URL has already been submitted."
    }

    # Don't show the empty label in the stance dropdown.
    stance = forms.ChoiceField(choices=Reference.STANCE_CHOICES,
                               initial=View.SUPPORT)

    # Use Australian date formatting.
    published_on = forms.DateField(
            label="Published",
            required=False,
            widget=forms.DateInput(
                    attrs={"placeholder": "dd/mm/yyyy (optional)"},
                    format="%d/%m/%Y"))

    # Show placeholder text in the URL field...
    url = forms.CharField(label="URL", widget=forms.TextInput(attrs={
            "placeholder": "http://example.com/"
    }))

    # ...and in the text field.
    text = forms.CharField(required=False, widget=forms.Textarea(attrs={
            "placeholder": "Brief summary of the reference (optional)."
    }))

    class Meta:
        model = Reference
        exclude = ("author", "is_archived", "score", "text_html", "view")

    def clean(self):
        """Ensure that ``url`` is unique within the stance."""
        stance = self.cleaned_data.get("stance")
        url = self.cleaned_data.get("url")

        if stance and url:
            try:
                # Retrieve duplicate references (excluding this one). An
                # exception will be raised if the instance doesn't have a view.
                duplicates = self.instance.view.reference_set.filter(
                        stance=stance, url=url).exclude(pk=self.instance.pk)
            except View.DoesNotExist:
                raise Exception("ReferenceForm must be passed a Reference.")

            if len(duplicates) > 0:
                message = self._ERROR_MESSAGES["DUPLICATE_URL"]
                self._errors["url"] = self.error_class([message])
                del self.cleaned_data["url"]

        return self.cleaned_data


class UserForm(forms.ModelForm):
    """A user registration form."""

    _ERROR_MESSAGES = {
        "EXISTING_EMAIL": "That email is already in use.",
        "PASSWORD_MISMATCH": "The passwords don't match.",
        "REQUIRED": "This field is required.",
    }

    first_name = forms.CharField(label="First Name")
    last_name = forms.CharField(label="Last Name")
    email = forms.EmailField()
    password = forms.CharField(required=False, widget=forms.PasswordInput)
    password_confirmation = forms.CharField(label="Password Again",
            required=False, widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "password")

    def __init__(self, request, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields["captcha"] = ReCAPTCHAField(request, label="CAPTCHA")

    def clean_email(self):
        """Ensures that ``email`` is unique."""
        email = self.cleaned_data["email"]
        users = User.objects.filter(email=email)

        if len(users) == 1 and users[0].pk != self.instance.pk:
            raise forms.ValidationError(self._ERROR_MESSAGES["EXISTING_EMAIL"])

        return email

    def clean(self):
        """Ensures that ``password`` and ``password_confirmation`` match."""
        password = self.cleaned_data.get("password")
        password_confirmation = self.cleaned_data.get("password_confirmation")

        # If we're creating a user or one password was given, both must be.
        if not self.instance.pk or (password or password_confirmation):
            error = self.error_class([self._ERROR_MESSAGES["REQUIRED"]])

            if not password:
                self._errors["password"] = error
                del self.cleaned_data["password"]

            if not password_confirmation:
                self._errors["password_confirmation"] = error
                del self.cleaned_data["password_confirmation"]

        # If they were both given, they must be the same.
        if password and password_confirmation:
            if password != password_confirmation:
                raise forms.ValidationError(
                        self._ERROR_MESSAGES["PASSWORD_MISMATCH"])

        return self.cleaned_data

    def save(self):
        """Sets the user's password and username before returning."""
        user = super(UserForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.username = self.cleaned_data["email"][:30]
        user.save()
        return user
