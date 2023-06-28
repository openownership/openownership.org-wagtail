from django.middleware.csrf import get_token
from django.utils.deprecation import MiddlewareMixin
from consoler import console  # NOQA


class CSRFCookieMiddleware(MiddlewareMixin):

    """Sets a CSRF cookie on every request
    """

    def process_response(self, request, response):
        get_token(request)  # Forces setting the CSRF cookie

        return response
