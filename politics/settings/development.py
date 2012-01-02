# coding=utf-8
from .common import *


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