# coding=utf-8
from .views import *
from django.conf.urls.defaults import include, patterns, url


# The pattern for slug URLs.
slug_pattern = r"^(?P<pk>\d+)/(?:(?P<slug>[a-z0-9_-]*)/)?$"

# /ajax/
ajax_patterns = patterns("",
    url(r"^tags/$", ajax.tags, name="tags"),
    url(r"^title/$", ajax.title, name="title"),
)

# /issues/
issue_patterns = patterns("",
    url(r"^$", issues.popular),
    url(r"^active/$", issues.active, name="active"),
    url(r"^(?P<pk>\d+)/edit/$", issues.form, name="edit"),
    url(r"^new/$", issues.form, name="new"),
    url(r"^popular/$", issues.popular, name="popular"),
    url(slug_pattern, issues.show, name="show"),
)

# /parties/
party_patterns = patterns("",
    url(r"^$", parties.list, name="list"),
    url(r"^new/$", parties.new, name="new"),
    url(slug_pattern, parties.show, name="show"),
)

# /references/
reference_patterns = patterns("",
    url(r"^(?P<pk>\d+)/comments/$", references.comments, name="comments"),
    url(r"^(?P<pk>\d+)/edit/$", references.edit, name="edit"),
    url(r"^(?P<pk>\d+)/votes/$", references.votes, name="votes"),
)

# /tags/
tag_patterns = patterns("",
    url(r"^$", tags.list, name="list"),
    url(slug_pattern, tags.show, name="show"),
)

# /users/
user_patterns = patterns("",
    url(r"^(?P<pk>\d+)/$", users.show, name="show"),
)

# /views/
view_patterns = patterns("",
    url(slug_pattern, views.show, name="show"),
    url(r"(?P<pk>\d+)/references/new/$", references.new, name="new-reference")
)

urlpatterns = patterns("",
    url(r"^$", issues.popular, name="home"),
    url(r"^about/$", core.about, name="about"),
    url(r"^contact/$", core.contact, name="contact"),
    url(r"^login/$", core.log_in, name="login"),
    url(r"^logout/$", core.log_out, name="logout"),
    url(r"^register/$", core.register, name="register"),
    url(r"^search/$", core.search, name="search"),
    url(r"^settings/$", core.settings, name="settings"),

    url(r"^ajax/", include(ajax_patterns, namespace="ajax")),
    url(r"^issues/", include(issue_patterns, namespace="issues")),
    url(r"^parties/", include(party_patterns, namespace="parties")),
    url(r"^references/", include(reference_patterns, namespace="references")),
    url(r"^tags/", include(tag_patterns, namespace="tags")),
    url(r"^users/", include(user_patterns, namespace="users")),
    url(r"^views/", include(view_patterns, namespace="views")),
)
