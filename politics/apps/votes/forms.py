# coding=utf-8
from .models import Vote
from django import forms


class VoteForm(forms.ModelForm):
    """A form for creating :class:`Vote`s."""

    class Meta:
        model = Vote
        fields = ("type",)
