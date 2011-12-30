# coding=utf-8
from django.contrib import admin
from django.conf.urls.defaults import patterns, include, url
from django.contrib.staticfiles.views import serve
from politics.apps.core.urls import urlpatterns as core_urlpatterns


admin.autodiscover()

urlpatterns = patterns("",
    # Library patterns.
    url(r"^auth/",  include("social_auth.urls")),
    url(r"^admin/", include(admin.site.urls)),

    # Our patterns.
    url(r"^", include(core_urlpatterns, namespace="core")),

    # Serve static media. This is horrendously slow and should be removed as
    # soon as possible, replaced with something like Amazon S3.
    url(r"^static/(?P<path>.*)$", serve, {"insecure": True})
)
