# coding=utf-8
from .models import *
from django.contrib import admin
from reversion.admin import VersionAdmin


class IssueAdmin(VersionAdmin):
    pass


# Register versioned models.
admin.site.register(Issue, IssueAdmin)

# Register other models.
models = (Party, Reference, Tag, UserProfile, View, Vote)
map(admin.site.register, models)
