# coding=utf-8
from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from politics.apps.api.urls import urlpatterns as api_urlpatterns
from politics.apps.comments.urls import urlpatterns as comments_urlpatterns
from politics.apps.core.urls import urlpatterns as core_urlpatterns
from politics.apps.feedback.urls import urlpatterns as feedback_urlpatterns


admin.autodiscover()

urlpatterns = patterns("",
    # Library patterns.
    url(r"^auth/",  include("social_auth.urls")),
    url(r"^admin/", include(admin.site.urls)),

    # Our patterns.
    url(r"^api/", include(api_urlpatterns, namespace="api")),
    url(r"^comments/", include(comments_urlpatterns, namespace="comments")),
    url(r"^feedback/", include(feedback_urlpatterns, namespace="feedback")),
    url(r"^", include(core_urlpatterns, namespace="core")),
)

if settings.DEBUG:
    urlpatterns += patterns("",
        url(r"^static/(?P<path>.*)$", "django.contrib.staticfiles.views.serve"),
        url(r"^media/(?P<path>.*)$", "django.views.static.serve", {
            "document_root": settings.MEDIA_ROOT
        })
    )
