# coding=utf-8
from django.contrib import admin
from django.conf.urls.defaults import patterns, include, url
from django.contrib.staticfiles.views import serve
from politics.apps.comments.urls import urlpatterns as comments_urlpatterns
from politics.apps.contribute.urls import urlpatterns as contribute_urlpatterns
from politics.apps.core.urls import urlpatterns as core_urlpatterns
from politics.apps.feedback.urls import urlpatterns as feedback_urlpatterns


admin.autodiscover()

urlpatterns = patterns("",
    # Library patterns.
    url(r"^auth/",  include("social_auth.urls")),
    url(r"^admin/", include(admin.site.urls)),

    # Our patterns.
    url(r"^comments/", include(comments_urlpatterns, namespace="comments")),
    url(r"^contribute/", include(contribute_urlpatterns, namespace="contribute")),
    url(r"^feedback/", include(feedback_urlpatterns, namespace="feedback")),
    url(r"^", include(core_urlpatterns, namespace="core")),

    # Serve static media. This is horrendously slow and should be removed as
    # soon as possible, replaced with something like Amazon S3.
    url(r"^static/(?P<path>.*)$", serve, {"insecure": True})
)
