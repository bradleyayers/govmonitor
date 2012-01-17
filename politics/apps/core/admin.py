# coding=utf-8
from .models import *
from django.contrib import admin
from reversion.admin import VersionAdmin


class IssueAdmin(VersionAdmin):
    pass


class ReferenceAdmin(VersionAdmin):
    pass


# Register versioned models.
admin.site.register(Issue, IssueAdmin)
admin.site.register(Reference, ReferenceAdmin)

# Register other models.
models = (Party, Tag, UserProfile, View, Vote)
map(admin.site.register, models)
