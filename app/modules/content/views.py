from typing import Optional

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
from modules.notion.models import CountryTag, Region
from modules.content.forms import SearchForm
from modules.content.models import content_page_models, HomePage, SectionPage
from modules.taxonomy.models import PrincipleTag, PublicationType, SectionTag, SectorTag


class DummyCountryPage(object):

    def __init__(self, country: CountryTag):
        self.country = country

    @cached_property
    def title(self):
        return self.country.name

    @cached_property
    def blurb(self):
        return self.country.blurb

    @cached_property
    def url(self):
        return self.country.url

    @cached_property
    def specific(self):
        return self

    def get_url(self):
        return self.url


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
    def breadcrumb_page(cls):
        """For pages that have a 'Back to ...' breadcrumb link, returns the page to
        go 'back' to. For most it's the parent, but some require going a bit higher;
        they can override this method.
        """
        from modules.content.models import MapPage
        try:
            return MapPage.objects.filter(locale=Locale.get_active()).first()
        except Exception as e:
            console.warn(e)
            return

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
        self.filter_mode = 'or'

        # Will be the search terms:
        self.terms = ''

        # We'll save all the taxonomy objects in here:
        self.filters = {}
        # And a list of them all in here:
        self.filters_list = []
        # Were any filters chosen?
        self.is_filtered = False

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

        self._set_filters(request)

        super().setup(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        pages = self._get_pages(self.terms)

        self.paginator = self._get_paginator(pages)
        self.page_obj = self.paginator
        context['form'] = SearchForm(initial={
            'q': self.terms,
            'pt': self.request.GET.getlist('pt', []),
            'pr': self.request.GET.getlist('pr', []),
            'sn': self.request.GET.getlist('sn', []),
            'sr': self.request.GET.getlist('sr', []),
            'co': self.request.GET.getlist('co', []),
        })
        context['terms'] = self.terms
        context['page'] = self
        context['results'] = self.paginator
        context['filters_list'] = self.filters_list

        # Add regions and their countries to help us split up the country
        # checkboxes by region.
        context['regions'] = []
        for region in Region.objects.all():
            context['regions'].append({
                'name': region.name,
                'countries': list(region.countries.values_list('id', flat=True))
            })

        if self.terms:
            context['meta_title'] = f"Search: {self.terms}"
        else:
            context['meta_title'] = "Search"
        global_context(context)  # Adds in nav settings etc.
        return context

    def _set_filters(self, request):
        """
        Gets all the taxonomy objects based on the chosen filters.
        Will be used when getting the queryset.
        """
        f = {}  # for brevity

        ids = [int(n) for n in request.GET.getlist('pt', [])]
        f['publication_types'] = PublicationType.objects.filter(id__in=ids)
        self.filters_list += list(f['publication_types'])

        ids = [int(n) for n in request.GET.getlist('pr', [])]
        f['principle_tags'] = PrincipleTag.objects.filter(id__in=ids)
        self.filters_list += list(f['principle_tags'])

        ids = [int(n) for n in request.GET.getlist('sn', [])]
        f['section_tags'] = SectionTag.objects.filter(id__in=ids)
        self.filters_list += list(f['section_tags'])

        ids = [int(n) for n in request.GET.getlist('sr', [])]
        f['sector_tags'] = SectorTag.objects.filter(id__in=ids)
        self.filters_list += list(f['sector_tags'])

        ids = [int(n) for n in request.GET.getlist('co', [])]
        f['country_tags'] = CountryTag.objects.filter(id__in=ids)
        self.filters_list += list(f['country_tags'])

        self.filters = f

        if len(self.filters_list) > 0:
            self.is_filtered = True

    def _get_paginator(self, results):
        p = Paginator(results, 10)
        result_set = p.page(self.page_num)
        return result_set

    def _get_pages(self, terms):
        query = Query.get(terms)
        query.add_hit()

        promoted = Query.get(terms).editors_picks.all()
        exclude_ids = [p.id for p in promoted]

        qs = Page.objects

        if self.is_filtered:
            page_ids = []

            def add_ids(a, b):
                "Combines and returns two lists of IDs, a and b."
                if self.filter_mode == 'and' and len(a) > 0:
                    # a will contain only IDs that are in BOTH lists
                    a = list(set(a).intersection(b))
                else:
                    # a will contain all of the IDS:
                    a += b
                return a

            f = self.filters  # for brevity

            # The publication_types Category:

            if len(f['publication_types']):
                for pt in f['publication_types']:
                    ids = list(pt.pages.values_list('id', flat=True))
                    page_ids = add_ids(page_ids, ids)

            # The three Tags:

            if len(f['principle_tags']):
                for tag in f['principle_tags']:
                    ids = list(tag.principle_tag_related_pages.values_list('content_object__id', flat=True))
                    page_ids = add_ids(page_ids, ids)

            if len(f['section_tags']):
                for tag in f['section_tags']:
                    ids = list(tag.section_tag_related_pages.values_list('content_object__id', flat=True))
                    page_ids = add_ids(page_ids, ids)

            if len(f['sector_tags']):
                for tag in f['sector_tags']:
                    ids = list(tag.sector_related_pages.values_list('content_object__id', flat=True))
                    page_ids = add_ids(page_ids, ids)

            if len(f['country_tags']):
                for tag in f['country_tags']:
                    ids = list(tag.country_related_pages.values_list('content_object__id', flat=True))
                    page_ids = add_ids(page_ids, ids)

            # Restrict to the only page types that have taxonomies
            # and filter by the page_ids we've found.
            qs = qs.type(*content_page_models).filter(id__in=set(page_ids))

        searched = (
            qs.exclude(id__in=exclude_ids)
            .filter(locale=Locale.get_active())
            .live().specific()
        )

        if terms:
            searched = searched.search(terms, operator=self.mode)

        # Check to see if this matches a Country name
        countries = self._find_countries(terms)
        # Unify stuff
        objects = []
        objects += countries
        objects += [r.page for r in promoted]
        if searched:
            objects = objects + [r for r in searched]
            return objects
        else:
            return objects

    def _find_countries(self, terms: str) -> Optional[DummyCountryPage]:
        rv = []
        if not len(terms):
            return []
        try:
            countries = CountryTag.objects.filter(name__icontains=terms).all()
            if not countries:
                return rv

            for country in countries:
                rv.append(DummyCountryPage(country))
            return rv

        except Exception as e:
            console.warn(e)

        return rv
