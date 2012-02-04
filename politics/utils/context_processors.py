# coding=utf-8
from django.conf import settings


def google_analytics(request):
    """Adds the site's Google Analytics tracking ID to the context."""
    # The ID won't be available if we're running in development mode as it's
    # defined in the production settings file. Use None as a default.
    key = "GOOGLE_ANALYTICS_TRACKING_ID"
    return {key: getattr(settings, key, None)}
