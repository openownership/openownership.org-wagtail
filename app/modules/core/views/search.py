from itertools import chain

from django.conf import settings
from django.views.generic import ListView

from wagtail.core.models import Page, Site
from wagtail.search.models import Query

from modules.core.models.settings import (
    SocialMediaSettings, AnalyticsSettings
)


class SearchView(ListView):

    context_object_name = 'objects'
    page = 1
    paginate_by = 20
    search_query = None
    search_results = []
    template_name = 'search/results.jinja'
    cache_control = 'no-cache'

    def dispatch(self, *args, **kwargs):
        self.search_query = self.request.GET.get('query', None)
        self.page = self.request.GET.get('page', 1)

        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        site = Site.objects.get(is_default_site=True)
        context.update(**SocialMediaSettings.get_for_context(site))
        context.update(**AnalyticsSettings.get_for_context(site))

        context.update({
            'search_query': self.search_query,
            'meta_title': f'Search: {self.search_query}',
            'site_name': settings.SITE_NAME
        })

        return context

    def get_queryset(self):
        if self.search_query:
            query = Query.get(self.search_query)
            promoted_ids = query.editors_picks.values_list('page_id', flat=True)
            if promoted_ids:
                promoted_pages = Page.objects.filter(id__in=promoted_ids).live().specific()
            else:
                promoted_pages = Page.objects.none()

            pages = Page.objects\
                        .specific()\
                        .live()\
                        .exclude(id__in=promoted_ids)\
                        .search(self.search_query)

            search_results = list(chain(promoted_pages, pages))
            query.add_hit()
        else:
            search_results = Page.objects.none()

        self.search_results = search_results

        return search_results
