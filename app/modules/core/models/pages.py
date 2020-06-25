# -*- coding: utf-8 -*-

"""
    core.models.pages
    ~~~~~~~~~~~~~~~~~
    Site-wide page modules.
"""

from itertools import chain

# 3rd party
from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

from django.db import models
from django.template.response import TemplateResponse
from django.utils.functional import cached_property

from modelcluster.fields import ParentalKey

from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel, InlinePanel, PageChooserPanel
from wagtail.core import fields
from wagtail.core.models import Orderable, Page
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search.models import Query

from wagtail.utils.decorators import cached_classmethod

# Project

from config.template import url_from_path
from modules.core.blocks import (
    home_page_blocks, landing_page_blocks
)

from .page_types import BasePage, LandingPageType, ContentPageType, ArticlePageWithContentsType


####################################################################################################
# Landing type pages
####################################################################################################


class HomePage(LandingPageType):

    class Meta:
        verbose_name = 'Home page'

    template: str = 'core/home.jinja'
    search_fields: list = []

    body = fields.StreamField(home_page_blocks, blank=True)

    def get_context(self, request, *args, **kwargs) -> dict:
        context = super().get_context(request, *args, **kwargs)
        context['body_classes'] = 'home-page'
        context['is_home'] = True
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
    template = 'core/landing_page.jinja'


####################################################################################################
# Content type pages
####################################################################################################

class ArticlePage(ContentPageType):
    template = 'core/article_page.jinja'


class ApplicationGuidancePage(ArticlePageWithContentsType):
    template = 'core/article_page_with_contents.jinja'


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

    # link_page_anchor = models.CharField(
    #     help_text='Jump to an anchor on a linked page',
    #     null=True,
    #     blank=True,
    #     max_length=255
    # )

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
        'core.SearchPage',
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
    parent_page_types = ['core.HomePage', ]
    objects_per_page = 10

    suggested_searches_title = models.CharField(
        null=True,
        blank=False,
        max_length=255,
        default="People commonly search for"
    )

    content_panels = BasePage.content_panels + [
        FieldPanel('suggested_searches_title', classname="title"),
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


####################################################################################################
# Legal / Cookies
####################################################################################################

class CookiesPage(BasePage):

    cache_control = 'no-cache'

    template = 'core/cookies_page.jinja'

    page_intro = fields.RichTextField(
        features=['bold', 'italic', 'underline', 'small', 'link', 'document-link']
    )

    analytics_intro = fields.RichTextField(
        features=['bold', 'italic', 'underline', 'small', 'link', 'document-link']
    )

    third_party_intro = fields.RichTextField(
        features=['bold', 'italic', 'underline', 'small', 'link', 'document-link']
    )

    content_panels = BasePage.content_panels + [
        FieldPanel('page_intro'),
        FieldPanel('analytics_intro'),
        FieldPanel('third_party_intro'),
    ]

    parent_page_types: list = ['core.HomePage', ]

    def get_form(self, *args, **kwargs):
        from modules.core.forms import CookiesForm
        form_class = CookiesForm
        return form_class(*args, **kwargs)

    def serve(self, request, *args, **kwargs):
        from modules.core.forms import CookiesForm
        template = self.get_template(request, *args, **kwargs),
        context = self.get_context(request)
        context['cookie_types'] = CookiesForm.COOKIE_TYPES

        if request.method == 'POST':
            form = self.get_form(request.POST, cookies=request.COOKIES)

            if form.is_valid():
                context.update({
                    'form': form,
                    'show_success_message': True
                })
                response = TemplateResponse(request, template, context)

                for field, value in form.cleaned_data.items():
                    response.set_cookie(field, value)

                return response

        else:
            form = self.get_form(cookies=request.COOKIES)
            context['form'] = form

            return TemplateResponse(request, template, context)

    def serve_preview(self, request, mode):
        return super().serve_preview(request, mode)

    @classmethod
    def can_create_at(cls, parent) -> bool:
        return super().can_create_at(parent) and not cls.objects.exists()
