# coding=utf-8
import os
import os.path
import site
import sys


# The root of the project.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Use our virtual environment.
site.addsitedir(os.path.join(ROOT, "environment/lib/python2.7/site-packages"))

# Set up Django's settings.
sys.path.append(ROOT)
os.environ["DJANGO_SETTINGS_MODULE"] = "politics.settings"

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()