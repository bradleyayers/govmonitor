# coding=utf-8
"""This module integrates third-party libraries with South.

Libraries don't always support South out of the box; we need to add
introspection rules if the use custom model fields, and we need somewhere to
store migrations if they provide models. This app solves both these problems.
"""
try:
    from south.modelsinspector import add_introspection_rules

    # social_auth
    add_introspection_rules([], ["^social_auth\.fields\.JSONField"])
except ImportError:
    pass
