# coding=utf-8
from django.conf.urls.defaults import patterns, url
from politics.apps.comments.views import *


urlpatterns = patterns("",
    url("^(?P<pk>\d+)/$", comment, name="comment"),
)
