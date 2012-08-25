# coding=utf-8
from .views import *
from django.conf.urls.defaults import include, patterns, url
from politics.utils.urls import prefix

# /issues/{pk}/
issue_prefix = r"^(?P<pk>\d+)/"
issue_patterns = prefix(issue_prefix, patterns("",
    url(r"$", issues.show, name="show")
))

urlpatterns = patterns("",
    url(r"^issues/", include(issue_patterns, namespace="issues"))
)