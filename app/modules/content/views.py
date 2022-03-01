# 3rd party
from consoler import console
from django.conf import settings
from django.http import Http404
from django.utils.text import slugify
from wagtail.core.models import Locale, Page
from django.views.generic import TemplateView
from django.core.paginator import Paginator
from wagtail.search.models import Query
from django.utils.functional import cached_property
from django.utils.datastructures import MultiValueDictKeyError

# Project
from config.template import author_url
from helpers.context import global_context
from modules.notion.models import CountryTag
from modules.content.models import HomePage, SectionPage


class CountryView(TemplateView):

    template_name = 'views/country.jinja'

    def __init__(self, *args, **kwargs):
        self.page_num = 1

    def setup(self, request, *args, **kwargs):
        try:
            self.page_num = int(request.GET['page'])
        except MultiValueDictKeyError:
            self.page_num = 1
        except Exception as e:
            console.error(e)
        super().setup(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = kwargs.pop('slug')
        self.tag = self._get_tag(slug)
        context['country'] = self.tag
        context['page'] = self
        context['meta_title'] = f"{self.tag.name}"
        global_context(context)  # Adds in nav settings etc.
        return context

    @cached_property
    def title(self):
        return self.tag.name

    @cached_property
    def section_page(self):
        """Country views appear as though inside the Impact section, so we look this up
        for the menu etc. first for the current locale, secondly for any locale, and
        if it fails to find one, it returns the HomePage just so that there's something.
        """
        try:
            page = SectionPage.objects.filter(locale=Locale.get_active(), slug='impact').get()
        except SectionPage.DoesNotExist:
            page = SectionPage.objects.filter(slug='impact').first()
            if not page:
                page = HomePage.objects.filter(locale=Locale.get_active()).first()

        return page

    def _get_tag(self, slug):
        try:
            tag = CountryTag.objects.get(slug=slug)
        except CountryTag.DoesNotExist:
            raise Http404
        else:
            return tag


class SearchView(TemplateView):

    template_name = 'search/results.jinja'

    def __init__(self, *args, **kwargs):
        self.page_num = 1
        self.mode = 'and'
        self.terms = ''

    def setup(self, request, *args, **kwargs):
        try:
            self.page_num = int(request.GET['page'])
        except MultiValueDictKeyError:
            self.page_num = 1
        except Exception as e:
            console.error(e)
        try:
            self.terms = str(request.GET['q'])
        except MultiValueDictKeyError:
            self.terms = ''
        except Exception:
            self.terms = ''

        super().setup(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pages = self._get_pages(self.terms)
        self.paginator = self._get_paginator(pages)
        self.page_obj = self.paginator
        context['terms'] = self.terms
        context['page'] = self
        context['results'] = self.paginator

        if self.terms:
            context['meta_title'] = f"Search: {self.terms}"
        else:
            context['meta_title'] = "Search"
        global_context(context)  # Adds in nav settings etc.
        return context

    def _get_paginator(self, results):
        p = Paginator(results, settings.PAGINATOR['objects_per_page'])
        result_set = p.page(self.page_num)
        return result_set

    def _get_pages(self, terms):
        query = Query.get(terms)
        query.add_hit()
        promoted = Query.get(terms).editors_picks.all()
        exclude_ids = [p.id for p in promoted]
        searched = Page.objects.exclude(
            id__in=exclude_ids).filter(
            locale=Locale.get_active()
        ).live().specific().search(terms, operator=self.mode)

        # Unify stuff
        objects = []
        objects += [r.page for r in promoted]
        if searched:
            objects = objects + [r for r in searched]
            return objects
        else:
            return objects


class DummyUserPage(object):

    def __init__(self, user):
        self.user = user

    @property
    def display_type(self):
        return "Profile"

    @cached_property
    def title(self):
        return self.user.full_name

    @cached_property
    def blurb(self):
        return self.user.bio

    @cached_property
    def excerpt(self):
        return self.user.bio

    @cached_property
    def url(self):
        return author_url(self.user.slug)

    @cached_property
    def thumb(self):
        return self.user.avatar

    @cached_property
    def specific(self):
        return self

    @cached_property
    def thumbnail(self):
        return self.thumb

    @cached_property
    def default_image(self):
        if self.thumb:
            return self.thumb
        else:
            from modules.core.models.settings import DefaultImageSettings
            try:
                default_image = DefaultImageSettings.objects.first()
                return default_image.image
            except Exception:
                return None

    def get_excerpt(self):
        return self.blurb
