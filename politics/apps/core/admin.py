# coding=utf-8
from .models import *
from django.contrib import admin
from reversion.admin import VersionAdmin


# Register versioned models whose history is to be shown in the administration
# interface. ``reversion.register`` is enough if you don't want to see history.
admin.site.register(Issue, VersionAdmin)
admin.site.register(Reference, VersionAdmin)
admin.site.register(View, VersionAdmin)

# Register other models.
models = (Election, Party, Tag, UserProfile)
map(admin.site.register, models)