# coding=utf-8
from django.conf.urls.defaults import patterns, url
from politics.apps.feedback.views import *


urlpatterns = patterns("",
    url("^$", feedback, name="feedback"),
)
