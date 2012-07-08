# coding=utf-8
from celery.schedules import crontab
from celery.task import periodic_task
from django.core.mail import mail_admins
from django.db import transaction
from django.db.models import Count
from django.utils.log import AdminEmailHandler
from djcelery_transactions import task
import logging
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


@task(ignore_result=True)
@transaction.commit_on_success
def calculate_view_notability(view_pk):
    """Calculate a view's notability.

    .. note::

        If the party's stance is unknown, the view's notability will be 0.

    :param view_pk: The view's primary key.
    :type  view_pk: ``int``
    """
    def _calculate_stance_rarity(view):
        """Calculate the rarity of a party's stance on an issue.

        This identifies cases where we have little/no information about other
        parties' stances on an issue: a sign that it's specific to one party.

        :returns: 1 if the stance is rare, 0 if it's not.
        """
        is_rare = view.issue.view_set.exclude(stance=View.UNKNOWN).count() == 1
        return 0.6 if is_rare else 0

    def _calculate_stance_uniqueness(view):
        """Calculate the uniqueness of a party's stance on an issue.

        This identifies stances that differ from the prevailing stance of other
        parties (e.g. all parties but this one support the issue in question).

        :returns: A value in the range 0-1 describing the stance's uniqueness;
                  a larger value indicates that the stance is "more unique."
        """
        views = view.issue.view_set.exclude(stance=View.UNKNOWN)
        views = views.values("stance").annotate(count=Count("stance"))

        equal_count = views.filter(stance=view.stance)[0]["count"]
        prevailing_count = views.order_by("-count")[0]["count"]
        return 1 - equal_count / float(prevailing_count)

    view = View.objects.get(pk=view_pk)
    if view.stance == View.UNKNOWN:
        view.notability = 0
        view.save(touch_updated_at=False)
        return

    # These functions take a View and return a score for some metric of
    # notability. These scores are combined to arrive at the total notability.
    score_calculators = [
        _calculate_stance_rarity,
        _calculate_stance_uniqueness
    ]

    scores = [calculator(view) for calculator in score_calculators]
    view.notability = max(scores)
    view.save(touch_updated_at=False)


@periodic_task(ignore_result=True, run_every=crontab(hour=0, minute=0))
@transaction.commit_on_success
def delete_unused_tags():
    """Deletes unused tags from the database.

    Run at midnight every day.
    """
    tags = Tag.objects.annotate(issue_count=Count("issue"))
    tags.filter(issue_count=0).delete()


@task(ignore_result=True)
def email_log_record(record):
    """Emails a log record to the site admins.

    If ``record`` is an error, Django's default email handler is used as it
    prints the exception, request, etc. Otherwise, the record's ``body``
    attribute is used as the body of the email (if set).

    :param record: The log record.
    :type  record: ``logging.LogRecord``
    """
    if record.levelno >= logging.ERROR:
        AdminEmailHandler().emit(record)
    else:
        mail_admins(record.getMessage(), getattr(record, "body", ""))
