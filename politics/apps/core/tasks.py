# coding=utf-8
from celery.schedules import crontab
from celery.task import periodic_task
from django.db import transaction
from django.db.models import Count
from djcelery_transactions import task
from politics.apps.core.models import Party, PartySimilarity, Tag, View


@task(ignore_result=True)
@transaction.commit_on_success
def calculate_party_similarities(party_pk):
    """Calculate a party's similarity with every other party.

    A new :class:`PartySimilarity` object is created for each result.

    :param party_pk: The party's primary key.
    :type  party_pk: ``int``
    """
    # Returns a party's (known) views as a set of issue/stance tuples.
    def _get_party_view_set(party):
        views = View.objects.filter(party=party).exclude(stance=View.UNKNOWN)
        return set(views.values_list("issue", "stance"))

    party = Party.objects.get(pk=party_pk)
    party_views = _get_party_view_set(party)
    party_issues = set(view[0] for view in party_views)

    # Archive existing PartySimilarity objects.
    PartySimilarity.objects.filter(first_party=party).update(is_archived=True)

    for other_party in Party.objects.exclude(pk=party_pk):
        other_party_views = _get_party_view_set(other_party)
        other_party_issues = set(view[0] for view in other_party_views)

        # Extract common views and determine the maximum possible similarity:
        # we can only compare views where we have information on both parties.
        common_views = party_views & other_party_views
        maximum_similarity = len(party_issues & other_party_issues)

        # If there's no overlap in their issues, similarity is undefined;
        # otherwise, create a PartySimilarity object to store the result.
        if maximum_similarity > 0:
            similarity = len(common_views) / float(maximum_similarity)
            PartySimilarity(first_party=party, second_party=other_party,
                            similarity=similarity).save()


@periodic_task(run_every=crontab(hour=0, minute=0))
@transaction.commit_on_success
def delete_unused_issues():
    """Deletes unused tags from the database.

    Run at midnight every day.
    """
    tags = Tag.objects.annotate(issue_count=Count("issue"))
    tags.filter(issue_count=0).delete()
