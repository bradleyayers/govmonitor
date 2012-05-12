# coding=utf-8
from django.conf.urls.defaults import patterns, url
from politics.apps.contribute.views import *


urlpatterns = patterns("",
    url("^$", index, name="index"),
    url("^skip/$", skip, name="skip"),
)
