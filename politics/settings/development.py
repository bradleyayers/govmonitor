# coding=utf-8
from .common import *


# -----------------------------------------------------------------------------
# Caching
# -----------------------------------------------------------------------------

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.memcached.PyLibMCCache",
        "LOCATION": "127.0.0.1:11212"
    }
}

# -----------------------------------------------------------------------------
# Database
# -----------------------------------------------------------------------------

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "HOST": "",
        "NAME": os.path.join(ROOT, "database.sqlite3"),
        "PASSWORD": "",
        "USER": "",
    }
}

# -----------------------------------------------------------------------------
# General
# -----------------------------------------------------------------------------

DEBUG = True
TEMPLATE_DEBUG = True
