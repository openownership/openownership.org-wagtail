from wagtail.core.models import Site
from modules.stats.models import ViewCount


class ViewCountMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response
        self.skip = ['admin', 'static', 'media']
        # TODO: Make the skip list into an overridable setting

    def __call__(self, request):
        page = self._find_page_from_path(request, request.path)
        if page and hasattr(page, 'is_countable') and page.is_countable is True:
            ViewCount.objects.hit(page.id)

        response = self.get_response(request)
        return response

    def _find_page_from_path(self, request, path):
        site = Site.find_for_request(request)
        path_components = [component for component in path.split('/') if component]
        if len(path_components) == 0:
            return
        if path_components[0] in self.skip:
            return
        page, args, kwargs = site.root_page.specific.route(request, path_components)
        return page
