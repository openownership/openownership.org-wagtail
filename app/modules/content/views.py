from itertools import chain

from django.db.models import Case, When
from django.conf import settings
from django.views.generic import ListView

from wagtail.core.models import Page, Site
from wagtail.search.models import Query

from django.http import Http404
from modules.content.models.mixins import AppPageContextMixin
from modules.content.models import NewsCategory

from .models import (
    NewsArticlePage
)


class IndexViewMixin(AppPageContextMixin, ListView):

    context_object_name = 'objects'
    paginate_by = 20
    object_model = None
    order_by = ['-display_date', 'last_published_at']

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)

        context.update({
            'highlight_first': int(self.request.GET.get(self.page_kwarg, 1)) == 1,
            'page_kwarg': self.page_kwarg
        })

        return context

    def get_queryset(self):

        query = self.model.objects\
            .select_related('thumbnail')\
            .live()

        return query.distinct().order_by(*self.order_by)


class NewsIndexPageView(AppPageContextMixin, ListView):

    template_name = "content/news_index_page.jinja"
    context_object_name = 'objects'
    paginate_by = 20
    current_page = 1
    featured_ids = []

    def dispatch(self, *args, **kwargs):
        parent = self.parent_page
        self.current_page = self.request.GET.get('page', 1)
        self.featured_ids = list(parent.featured_articles.values_list('link_page_id', flat=True))
        return super().dispatch(*args, **kwargs)

    def get_featured_articles(self):

        preserved_order = Case(*[
            When(pk=pk, then=pos) for pos, pk in enumerate(self.featured_ids)
        ])

        featured = (
            NewsArticlePage.objects
                           .filter(pk__in=self.featured_ids)
                           .live()
                           .select_related('thumbnail')
                           .order_by(preserved_order)
        )

        return featured

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)

        featured_articles = self.get_featured_articles()

        categories = (
            NewsCategory.objects
                        .filter(news__live=True)
                        .distinct()
                        .values_list('slug', 'name')
        )

        context.update({
            'categories': list(categories),
            'category_slug': self.kwargs.get('category_slug', 'latest'),
            'highlight_first': int(self.request.GET.get(self.page_kwarg, 1)) == 1,
            'page_kwarg': self.page_kwarg
        })

        if self.current_page == 1 and self.featured_ids:
            context['featured_articles'] = featured_articles

        return context

    def get_queryset(self):

        query = (
            NewsArticlePage
            .objects
            .descendant_of(self.parent_page)
            .exclude(id__in=self.featured_ids)
            .live()
            .select_related('thumbnail')
        )

        category_slug = self.kwargs.get('category_slug', None)
        if category_slug:
            if NewsCategory.objects.filter(slug=category_slug).exists():
                query = query.filter(categories__slug=self.kwargs.get('category_slug'))
            else:
                raise Http404()

        return query.distinct().order_by('-display_date', '-last_published_at')


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
        # context.update(**SocialMediaSettings.get_for_context(site))
        # context.update(**AnalyticsSettings.get_for_context(site))

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
