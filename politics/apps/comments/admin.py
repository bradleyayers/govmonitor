# coding=utf-8
from django.contrib import admin
from politics.apps.comments.models import Comment
from reversion.admin import VersionAdmin


admin.site.register(Comment, VersionAdmin)
