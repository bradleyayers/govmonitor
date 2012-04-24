# coding-utf-8
from django.http import QueryDict
from django.http.multipartparser import MultiValueDict


class RESTMiddleware(object):
    """Patches incoming requests with ``DELETE`` and ``PUT`` properties."""

    def process_request(self, request):
        """Patch the incoming request.

        :param request: The incoming HTTP request.
        :type  request: ``django.http.HttpRequest``
        """
        request.DELETE = QueryDict("")
        request.PUT = QueryDict("")

        method = request.method.upper()
        if method in ("DELETE", "PUT"):
            data, request._files = self._parse_request(request)
            setattr(request, method, data)

    def _parse_request(self, request):
        content_type = request.META.get("CONTENT_TYPE", "")
        is_multipart = content_type.startswith("multipart")

        if is_multipart:
            return request.parse_file_upload(request.META, request)
        else:
            return (QueryDict(request.raw_post_data), MultiValueDict())
