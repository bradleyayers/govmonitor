# coding=utf-8
from .models import Task
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from politics.apps.core.forms import ReferenceForm
from politics.apps.core.models import Reference, View
from politics.utils.decorators import render_to_template
from politics.utils.views import login_path
import logging
import random
import reversion


def _assign_task(user):
    """Attempts to create a contribution task for the given user.

    .. note::

        No :class:`Task` will be created and ``None`` will be returned in the
        highly unlikely event that we don't have any tasks to be assigned.

    :param user: The user who is to be assigned a task.
    :type  user: ``django.contrib.auth.models.User``
    :returns: The newly created task, if one was created.
    :rtype: ``politics.apps.contribute.models.Task`` or ``None``
    """
    # Only consider thew views of root parties (not sub-parties).
    views = View.objects.filter(party__tree_level=0, stance=View.UNKNOWN)

    if len(views) > 0:
        task = Task(user=user, view=random.choice(views))
        task.save()
        return task


@login_required
@render_to_template("contribute/index.html")
def index(request):
    # Fetch the user's current task. If they don't have one, select one for
    # them. GET requests modifying state isn't ideal, but it's better UX.
    task = Task.objects.get_for_user(request.user)
    if task is None:
        task = _assign_task(request.user)

    completed_task = None
    form = ReferenceForm()

    if request.method == "POST":
        reference = Reference(author=request.user, view=task.view)
        form = ReferenceForm(request.POST, instance=reference)

        if form.is_valid():
            # Version the reference.
            with reversion.create_revision():
                reversion.set_user(request.user)
                reference = form.save()

            completed_task = task
            completed_task.is_complete = True
            completed_task.save()

            form = ReferenceForm()
            task = _assign_task(request.user)

            view = reference.view
            logging.getLogger("email").info("Reference Saved", extra={"body":
                "%s created a reference.\n\nhttp://govmonitor.org%s" % (
                    request.user.get_full_name(),
                    reverse("core:views:show", args=(view.pk, view.slug))
                )
            })

    return {"completed_task": completed_task, "form": form, "task": task}


def skip(request):
    """Skips the authenticated user's current task."""
    if not request.user.is_authenticated():
        return redirect(login_path(reverse("contribute:index")))

    _assign_task(request.user)
    return redirect("contribute:index")
