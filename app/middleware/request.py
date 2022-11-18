from collections import Counter
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from consoler import console


class AnalyticsMiddleware(MiddlewareMixin):

    """Not currently used, but may be expanded on in the future.
    """

    def process_request(self, request):
        # Create sessions for anonymous users
        if not request.session or not request.session.session_key:
            request.session.save()

        visits = request.session.get('visits', None)

        if visits is None:
            visits = Counter()

        visits.update([request.get_full_path(), ])
        request.session['visits'] = visits
        console.info(visits)

    def process_response(self, request, response):

        return response
