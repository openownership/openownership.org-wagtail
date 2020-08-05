from django.http import Http404
from django.utils.deprecation import MiddlewareMixin
from consoler import console
from wagtail.core.models import Site
from modules.stats.models import ViewCount


class ViewCountMiddleware(MiddlewareMixin):

    def _find_page_from_path(self, request, path):
        site = Site.find_for_request(request)
        if not site:
            raise Http404

        path_components = [component for component in path.split('/') if component]
        page, args, kwargs = site.root_page.specific.route(request, path_components)
        return page

    def process_request(self, request):
        page = self._find_page_from_path(request, request.path)
        if hasattr(page, 'is_countable') and page.is_countable is True:
            ViewCount.objects.hit(page.id)
