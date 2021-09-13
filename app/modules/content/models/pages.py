# -*- coding: utf-8 -*-

"""
    content.models.pages
    ~~~~~~~~~~~~~~~~~
    Site-wide page modules.
"""

from itertools import chain

# 3rd party
from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.forms import CheckboxSelectMultiple
from django.utils.functional import cached_property

from modelcluster.fields import ParentalKey, ParentalManyToManyField

from wagtail.admin.edit_handlers import (
    FieldPanel, InlinePanel, PageChooserPanel, StreamFieldPanel
)
from wagtail.core import fields
from wagtail.core.models import Orderable, Page
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search.models import Query

# Project

from config.template import url_from_path
from modules.content.blocks import home_page_blocks

from .page_types import BasePage, LandingPageType, ContentPageType, IndexPageType


####################################################################################################
# Landing type pages
####################################################################################################


class HomePage(LandingPageType):

    class Meta:
        verbose_name = 'Home page'

    template: str = 'content/home.jinja'
    search_fields: list = []

    body = fields.StreamField(home_page_blocks, blank=True)

    content_panels = BasePage.content_panels + [
        StreamFieldPanel('body')
    ]

    def get_context(self, request, *args, **kwargs) -> dict:
        context = super().get_context(request, *args, **kwargs)
        context['body_classes'] = 'home-page'
        context['is_home'] = True
        context.update(self.get_hero_context())
        return context

    def get_meta_title(self) -> str:
        meta_title = super().get_meta_title()
        if meta_title == 'Home':
            return settings.WAGTAIL_SITE_NAME
        return ""

    @classmethod
    def can_create_at(cls, parent) -> bool:
        return super().can_create_at(parent) and not cls.objects.exists()


class LandingPage(LandingPageType):
    template = 'content/landing_page.jinja'


####################################################################################################
# Content type pages
####################################################################################################

class ArticlePage(ContentPageType):
    template = 'content/article_page.jinja'


class UtilityPage(ContentPageType):
    template = 'content/utility_page.jinja'

    headline = models.CharField(
        help_text=(
            "If blank, the page title will be used",
        ),
        null=True,
        blank=True,
        max_length=255
    )

    intro = fields.RichTextField(
        blank=True,
        null=True,
    )

    content_panels = BasePage.content_panels + [
        FieldPanel('headline'),
        FieldPanel('intro')
    ] + ContentPageType.model_content_panels


####################################################################################################
# News (Latest) pages
####################################################################################################

class NewsIndexPage(IndexPageType):

    objects_model = 'content.NewsArticlePage'
    subpage_types = [objects_model, ]
    template = 'content/news_index_page.jinja'


class NewsArticlePage(ContentPageType):
    template = 'content/news_article_page.jinja'
    parent_page_types: list = ['content.NewsIndexPage', ]

    categories = ParentalManyToManyField(
        'content.NewsCategory',
        related_name="news",
        blank=True
    )

    content_panels = BasePage.content_panels + [
        FieldPanel('categories', widget=CheckboxSelectMultiple)
    ] + ContentPageType.model_content_panels

    @cached_property
    def category(self):
        return ', '.join([cat.name for cat in self.categories.all()])

    @cached_property
    def human_display_date(self):
        if self.display_date:
            return self.display_date.strftime('%d %B %Y')


####################################################################################################
# Search
####################################################################################################

class SearchPageSuggestedSearch(Orderable):

    link_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='suggested_for_search'
    )

    link_url = models.CharField(
        help_text='Link to an external URL',
        null=True,
        blank=True,
        max_length=255
    )

    text = models.CharField(
        null=True,
        blank=False,
        max_length=255
    )

    search_page = ParentalKey(
        'content.SearchPage',
        related_name='suggested_search_items',
        null=True,
        on_delete=models.CASCADE
    )

    panels = [
        FieldPanel('text'),
        PageChooserPanel('link_page'),
        FieldPanel('link_url'),
    ]


class SearchPage(BasePage):

    cache_control = 'no-cache'
    template = 'search.jinja'
    parent_page_types = ['content.HomePage', ]
    objects_per_page = 10

    headline = models.CharField(
        null=True,
        blank=False,
        max_length=255,
        default="Search all our content"
    )

    hero_image = models.ForeignKey(
        settings.IMAGE_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    suggested_searches_title = models.CharField(
        null=True,
        blank=False,
        max_length=255,
        default="People commonly search for"
    )

    content_panels = BasePage.content_panels + [
        FieldPanel('headline'),
        ImageChooserPanel('hero_image'),
        FieldPanel('suggested_searches_title'),
        InlinePanel('suggested_search_items', heading="Suggested pages")
    ]

    @cached_property
    def suggested_searches(self):
        objs = []
        for obj in self.suggested_search_items.select_related('link_page'):
            if obj.link_page:
                objs.append({
                    'text': obj.text,
                    'url': url_from_path(obj.link_page.url_path)
                })

            if obj.link_url:
                objs.append({
                    'text': obj.text,
                    'url': obj.link_url
                })

        return objs

    def get_results(self, search_query=None, page=1):

        objs = []
        if search_query:
            query = Query.get(search_query)
            promoted_ids = query.editors_picks.values_list('page_id', flat=True)
            if promoted_ids:
                promoted_pages = Page.objects.filter(id__in=promoted_ids).live().specific()
            else:
                promoted_pages = Page.objects.none()

            pages = Page.objects\
                        .specific()\
                        .live()\
                        .select_related('thumbnail_image')\
                        .exclude(id__in=promoted_ids)\
                        .search(search_query)

            objs = list(chain(promoted_pages, pages))
            query.add_hit()

        paginator = Paginator(objs, self.objects_per_page)

        try:
            search_results = paginator.page(page)
        except PageNotAnInteger:
            search_results = paginator.page(1)
        except EmptyPage:
            search_results = paginator.page(paginator.num_pages)

        return search_results

    def get_context(self, request, *args, **kwargs) -> dict:
        context = super().get_context(request, *args, **kwargs)
        search_query = request.GET.get('q', None)
        page = request.GET.get('page', 1)

        results = self.get_results(search_query, page)

        context.update({
            'search_query': search_query,
            'show_search': True,
            'results': results
        })

        if not results:
            context.update({
                'suggested_searches': self.suggested_searches
            })

        return context

    @classmethod
    def can_create_at(cls, parent) -> bool:
        return super().can_create_at(parent) and not cls.objects.exists()
