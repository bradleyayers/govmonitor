# coding=utf-8
import logging


class AsyncAdminEmailHandler(logging.Handler):
    """A logging handler that asynchronously sends emails.

    Dispatches a Celery task to send the email instead of blocking like the
    build-in handler. Standard Django email on error, simpler one otherwise.
    """

    def emit(self, record):
        """Dispatch the task.

        :param record: The log record.
        :type  record: ``logging.LogRecord``
        """
        from politics.apps.core.tasks import email_log_record


        email_log_record.delay(record)
