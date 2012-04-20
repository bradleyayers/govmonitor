# coding=utf-8
from django.forms import ModelForm
from politics.apps.comments.models import Comment


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ("body",)
