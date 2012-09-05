# coding=utf-8
from .views import *
from django.conf.urls.defaults import include, patterns, url
from politics.utils.urls import prefix


# /ajax/
ajax_patterns = patterns("",
    url(r"^tags/$", ajax.tags, name="tags"),
    url(r"^title/$", ajax.title, name="title"),
)

# /elections/{pk}-{slug}/
election_prefix = r"^(?P<pk>\d+)(?:-(?P<slug>[a-z0-9_-]*))?/"
election_patterns = prefix(election_prefix, patterns("",
    url(r"$", elections.show, name="show"),
    url(r"parties/$", elections.show, {"tab": "parties"}, name="show-parties")
))

# /elections/
elections_patterns = patterns("",
    url(r"^$", elections.list, name="list")
) + election_patterns

# /issues/{pk}-{slug}/
issue_prefix = r"^(?P<issue_pk>\d+)(?:-(?P<issue_slug>[a-z0-9_-]*))?/"
issue_patterns = prefix(issue_prefix, patterns("",
    url(r"$", issues.show, name="show"),
    url(r"edit/$", issues.form, name="edit"),
    url(r"parties/(?P<party_pk>\d+)(?:-(?P<party_slug>[a-z0-9_-]*))?/",
        views.show, name="view")
))

# /issues/
issues_patterns = patterns("",
    url(r"^$", issues.popular),
    url(r"^active/$", issues.active, name="active"),
    url(r"^new/$", issues.form, name="new"),
    url(r"^popular/$", issues.popular, name="popular"),
) + issue_patterns

# /parties/{pk}-{slug}/
party_prefix = r"^(?P<pk>\d+)(?:-(?P<slug>[a-z0-9_-]*))?/"
party_patterns = prefix(party_prefix, patterns("",
    url(r"$", parties.show, name="show"),
    url(r"edit/$", parties.form, name="edit"),
    url(r"parties/new/$", parties.new_child, name="new-child")
))

# /parties/
parties_patterns = patterns("",
    url(r"^$", parties.list, name="list"),
    url(r"^new/$", parties.form, name="new"),
) + party_patterns

# /references/
references_patterns = prefix(r"^(?P<pk>\d+)/", patterns("",
    url(r"comments/$", references.comments, name="comments"),
    url(r"edit/$", references.edit, name="edit"),
    url(r"votes/$", references.votes, name="votes"),
))

# /tags/{id}-{slug}/
tag_prefix = r"^(?P<pk>\d+)(?:-(?P<slug>[a-z0-9_-]*))?/"
tag_patterns = prefix(tag_prefix, patterns("",
    url(r"$", tags.show, name="show"),
))

# /tags/
tags_patterns = patterns("",
    url(r"^$", tags.list, name="list"),
) + tag_patterns

# /users/
users_patterns = patterns("",
    url(r"^(?P<pk>\d+)/$", users.show, name="show"),
)

urlpatterns = patterns("",
    url(r"^$", issues.popular, name="home"),
    url(r"^about/$", core.about, name="about"),
    url(r"^contact/$", core.contact, name="contact"),
    url(r"^faq/$", core.faq, name="faq"),
    url(r"^login/$", core.log_in, name="login"),
    url(r"^logout/$", core.log_out, name="logout"),
    url(r"^register/$", core.register, name="register"),
    url(r"^request/$", core.request, name="request"),
    url(r"^search/$", core.search, name="search"),
    url(r"^settings/$", core.settings, name="settings"),

    url(r"^ajax/", include(ajax_patterns, namespace="ajax")),
    url(r"^elections/", include(elections_patterns, namespace="elections")),
    url(r"^issues/", include(issues_patterns, namespace="issues")),
    url(r"^parties/", include(parties_patterns, namespace="parties")),
    url(r"^references/", include(references_patterns, namespace="references")),
    url(r"^tags/", include(tags_patterns, namespace="tags")),
    url(r"^users/", include(users_patterns, namespace="users")),
)
