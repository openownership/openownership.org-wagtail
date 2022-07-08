# 3rd party
from consoler import console
from wagtail.core.models import Site
from django.http.response import Http404
from django.utils.functional import cached_property
from wagtail.core.models.i18n import Locale

# Project
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
        # strip out the i18 slug
        if len(path_components) and path_components[0] in self._active_locale_slugs:
            path_components = path_components[1:]

        if len(path_components) == 0:
            return
        if path_components[0] in self.skip:
            return
        try:
            page, args, kwargs = site.root_page.specific.route(request, path_components)
        except Http404:
            console.warn(f"STATS: Failed to look up page at {path_components}")
        except Exception as e:
            console.warn(e)
        else:
            return page

    @cached_property
    def _active_locale_slugs(self):
        try:
            return [item.language_code for item in Locale.objects.all()]
        except Exception as e:
            console.warn(e)
