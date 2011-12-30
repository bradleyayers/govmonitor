# coding=utf-8
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from politics.utils.decorators import render_to_template


@render_to_template("core/users/show.html")
def show(request, pk):
    """Shows information about a user."""
    user = get_object_or_404(User, pk=pk)
    return {"user": user}
