# stdlib
import csv
from html import unescape
from typing import Optional

from consoler import console
from django.conf import settings
from django.core.paginator import EmptyPage, Paginator
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.functional import cached_property

# 3rd party
from django.utils.html import strip_tags
from django.views.generic import TemplateView
from django.views.generic.base import View
from wagtail.contrib.search_promotions.models import Query
from wagtail.models import Locale, Page, Site

# Project
from helpers.context import global_context
from modules.content.forms import SearchForm
from modules.content.models import (
    BotCentrePage,
    HomePage,
    PublicationInnerPage,
    SectionPage,
    content_page_models,
)
from modules.notion import evidence
from modules.notion.models import CountryTag, ImpactEntry, Region
from modules.settings.models import SiteSettings
from modules.stats.models import ViewCount
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
    def rich_blurb(self):
        return self.blurb

    @cached_property
    def url(self):
        return self.country.url

    @cached_property
    def specific(self):
        return self

    @cached_property
    def thumbnail(self):
        return self.country.map_image

    def get_url(self):
        return self.url


class DummyRegionPage(object):
    def __init__(self, region: Region):
        self.region = region

    @cached_property
    def title(self):
        return self.region.name

    @cached_property
    def specific(self):
        return self

    @cached_property
    def url(self):
        return reverse("region", kwargs={"slug": self.region.slug})

    def get_url(self):
        return self.url


class CountryView(TemplateView):
    template_name = "views/country.jinja"

    def __init__(self, *args, **kwargs):
        self.page_num = 1
        super().__init__(*args, **kwargs)

    def setup(self, request, *args, **kwargs):
        try:
            self.page_num = int(request.GET["page"])
        except MultiValueDictKeyError:
            self.page_num = 1
        except Exception as e:
            console.error(e)
        super().setup(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        slug = kwargs.pop("slug")
        self.tag = self._get_tag(slug)
        ctx["country"] = self.tag
        ctx["page"] = self
        ctx["meta_title"] = f"{self.tag.name}"
        ctx["meta_description"] = self._meta_description
        global_context(ctx)  # Adds in nav settings etc.
        # Add in pagination for related articles
        try:
            related_pages = self.tag.display_date_related_pages
            paginator = self._get_paginator(related_pages)
            ctx["results"] = paginator
            ctx["page_obj"] = paginator
        except Exception as e:
            console.warn(e)
        return ctx

    @cached_property
    def title(self):
        return self.tag.name

    @cached_property
    def _meta_description(self):
        try:
            meta_description = unescape(strip_tags(self.tag.blurb))
            meta_description = meta_description.replace("&#39;", "'")
        except Exception:
            meta_description = f"{self.tag.name} on Open Ownership"
        return meta_description

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
            return None

    @cached_property
    def section_page(self):
        """Country views appear as though inside the Impact section, so we look this up
        for the menu etc. first for the current locale, secondly for any locale, and
        if it fails to find one, it returns the HomePage just so that there's something.
        """
        try:
            page = SectionPage.objects.filter(locale=Locale.get_active(), slug="impact").get()
        except SectionPage.DoesNotExist:
            page = SectionPage.objects.filter(slug="impact").first()
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

    def _get_paginator(self, results):
        p = Paginator(results, 10)
        result_set = p.page(self.page_num)
        return result_set


class RegionView(TemplateView):
    template_name = "views/region.jinja"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        slug = kwargs.pop("slug")
        self.region = get_object_or_404(Region, slug=slug)
        ctx["region"] = self.region
        ctx["page"] = self
        ctx["meta_title"] = f"{self.region.name}"
        ctx["meta_description"] = self._meta_description
        ctx["country_list"] = self._get_countries()

        # For side menu
        ctx["page_menu_title"] = "Regions"
        ctx["menu_pages"] = self._get_menu_pages()

        global_context(ctx)  # Adds in nav settings etc.
        return ctx

    @cached_property
    def title(self):
        return self.region.name

    @cached_property
    def _meta_description(self):
        try:
            meta_description = unescape(strip_tags(self.region.blurb))
            meta_description = meta_description.replace("&#39;", "'")
        except Exception:
            meta_description = f"{self.region.name} on Open Ownership"
        return meta_description

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
            return None

    @cached_property
    def url(self):
        "To make this look more like a Page to the template."
        return reverse("region", kwargs={"slug": self.region.slug})

    @cached_property
    def section_page(self):
        """Region views appear as though inside the Impact section, so we look this up
        for the menu etc. first for the current locale, secondly for any locale, and
        if it fails to find one, it returns the HomePage just so that there's something.
        """
        try:
            page = SectionPage.objects.filter(locale=Locale.get_active(), slug="impact").get()
        except SectionPage.DoesNotExist:
            page = SectionPage.objects.filter(slug="impact").first()
            if not page:
                page = HomePage.objects.filter(locale=Locale.get_active()).first()

        return page

    def _get_countries(self):
        countries = self.region.countries.exclude(oo_support__isnull=True).order_by("name")
        return countries

    def _get_menu_pages(self):
        menu_pages = []
        for region in Region.objects.all().order_by("name"):
            menu_pages.append(DummyRegionPage(region))
        return menu_pages


class SearchView(TemplateView):
    template_name = "search/results.jinja"

    def __init__(self, *args, **kwargs):
        self.page_num = 1
        self.mode = "and"
        self.filter_mode = "or"

        # Will be the search terms:
        self.terms = ""

        # We'll save all the taxonomy objects in here:
        self.filters = {}
        # And a list of them all in here:
        self.filters_list = []
        # Were any filters chosen?
        self.is_filtered = False
        super().__init__(*args, **kwargs)

    def setup(self, request, *args, **kwargs):
        try:
            self.page_num = int(request.GET["page"])
        except MultiValueDictKeyError:
            self.page_num = 1
        except Exception as e:
            console.error(e)

        try:
            self.terms = str(request.GET["q"])
        except MultiValueDictKeyError:
            self.terms = ""
        except Exception:
            self.terms = ""

        self._set_filters(request)

        super().setup(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        pages = self._get_pages(self.terms)

        if not len(pages):
            context["popular"] = ViewCount.objects.popular_pages(count=6)

        self.paginator = self._get_paginator(pages)
        self.page_obj = self.paginator
        context["form"] = SearchForm(
            initial={
                "q": self.terms,
                "pt": self.request.GET.getlist("pt", []),
                "pr": self.request.GET.getlist("pr", []),
                "sn": self.request.GET.getlist("sn", []),
                "sr": self.request.GET.getlist("sr", []),
                "co": self.request.GET.getlist("co", []),
            },
        )
        context["terms"] = self.terms
        context["page"] = self
        context["results"] = self.paginator
        context["filters_list"] = self.filters_list

        # Add regions and their countries to help us split up the country
        # checkboxes by region.
        context["regions"] = []
        for region in Region.objects.all():
            context["regions"].append(
                {
                    "name": region.name,
                    "slug": region.slug,
                    "countries": list(region.countries.values_list("id", flat=True)),
                },
            )

        if self.terms:
            context["meta_title"] = f"Search: {self.terms}"
        else:
            site = Site.objects.get(is_default_site=True)
            search_body = SiteSettings.get_search_body(site)
            context["meta_title"] = "Search"
            context["search_body"] = search_body

        global_context(context)  # Adds in nav settings etc.
        return context

    def get_meta_title(self):
        if self.terms:
            return f"Search: {self.terms}"
        return "Search"

    # The filter parameters, each an id list, paired with what they select.
    FILTER_PARAMS = (
        ("pt", "publication_types", PublicationType),
        ("pr", "principle_tags", PrincipleTag),
        ("sn", "section_tags", SectionTag),
        ("sr", "sector_tags", SectorTag),
        ("co", "country_tags", CountryTag),
    )

    def _set_filters(self, request):
        """
        Gets all the taxonomy objects based on the chosen filters.
        Will be used when getting the queryset.
        """
        f = {}  # for brevity

        for param, key, model in self.FILTER_PARAMS:
            ids = self._ids(request.GET.getlist(param, []))
            f[key] = model.objects.filter(id__in=ids)
            self.filters_list += list(f[key])

        self.filters = f

        if len(self.filters_list) > 0:
            self.is_filtered = True

    @staticmethod
    def _ids(values) -> list:
        """The whole numbers among some query parameter values.

        This is a public URL, so a stale bookmark, a mangled share link or a
        crawler guessing at parameters has to show results rather than raise.
        Anything that is not a number is dropped, and the values beside it are
        still honoured.
        """
        ids = []
        for value in values:
            try:
                ids.append(int(value))
            except (TypeError, ValueError):
                continue
        return ids

    def _get_paginator(self, results):
        try:
            p = Paginator(results, 10)
            result_set = p.page(self.page_num)
        except EmptyPage as err:
            msg = "Page does not exist"
            raise Http404(msg) from err
        return result_set

    def _restrict(self, qs, exclude_ids):
        """Apply the shared result restrictions to a page queryset.

        Inner publication pages are excluded: their content is rolled up into
        the parent PublicationFrontPage index, so the parent surfaces instead
        of a child page mid-document.
        """
        return (
            qs.exclude(id__in=exclude_ids)
            .not_type(PublicationInnerPage)
            .filter(locale=Locale.get_active())
            .live()
            .specific()
        )

    def _get_pages(self, terms):
        if not terms or terms == "":
            qs = Page.objects.none()
            return qs

        query = Query.get(terms)
        query.add_hit()

        promoted = [item.page.specific for item in Query.get(terms).editors_picks.all()]
        exclude_ids = [p.id for p in promoted]

        qs = Page.objects

        if self.is_filtered:
            page_ids = []

            def add_ids(a, b):
                "Combines and returns two lists of IDs, a and b."
                if self.filter_mode == "and" and len(a) > 0:
                    # a will contain only IDs that are in BOTH lists
                    a = list(set(a).intersection(b))
                else:
                    # a will contain all of the IDS:
                    a += b
                return a

            f = self.filters  # for brevity

            # The publication_types Category:

            if len(f["publication_types"]):
                for pt in f["publication_types"]:
                    ids = list(pt.pages.values_list("id", flat=True))
                    page_ids = add_ids(page_ids, ids)

                # Ensure publication pages show when Publication is set as the content type
                # on a PublicationPage
                pub_type = PublicationType.objects.filter(slug="publication").first()
                if pub_type and pub_type in f["publication_types"]:
                    from modules.content.models.pages import PublicationFrontPage

                    ids = PublicationFrontPage.objects.live().public().values_list("id", flat=True)
                    page_ids = add_ids(page_ids, ids)

            # The three Tags:

            if len(f["principle_tags"]):
                for tag in f["principle_tags"]:
                    ids = list(
                        tag.principle_tag_related_pages.values_list(
                            "content_object__id",
                            flat=True,
                        ),
                    )
                    page_ids = add_ids(page_ids, ids)

            if len(f["section_tags"]):
                for tag in f["section_tags"]:
                    ids = list(
                        tag.section_tag_related_pages.values_list("content_object__id", flat=True),
                    )
                    page_ids = add_ids(page_ids, ids)

            if len(f["sector_tags"]):
                for tag in f["sector_tags"]:
                    ids = list(
                        tag.sector_related_pages.values_list("content_object__id", flat=True),
                    )
                    page_ids = add_ids(page_ids, ids)

            if len(f["country_tags"]):
                for tag in f["country_tags"]:
                    ids = list(
                        tag.country_related_pages.values_list("content_object__id", flat=True),
                    )
                    page_ids = add_ids(page_ids, ids)

            # Restrict to the only page types that have taxonomies
            # and filter by the page_ids we've found.
            qs = qs.type(*content_page_models).filter(id__in=set(page_ids))

        searched = self._restrict(qs, exclude_ids)

        if terms:
            searched = searched.search(terms, operator=self.mode)

        # Check to see if this matches a Country name
        countries = self._find_countries(terms)
        # Unify stuff
        objects = []
        objects += countries
        objects += promoted
        if searched:
            objects = objects + [r for r in searched]
            return objects
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


####################################################################################################
# Evidence Centre
####################################################################################################


class EvidenceDetailView(TemplateView):
    """One impact tracker record.

    The same view answers three ways. A normal request gets a whole page, which
    is what a reader arriving from a shared link or a search engine needs. A
    request carrying the `HX-Request` header gets the card on its own, so the
    listing can swap a record open where it sits. Adding `collapsed` to that
    asks for the card shut again, which is what the close control fetches.

    Entries are not Wagtail pages, so this is a plain Django view rather than a
    route on `BotCentrePage`.
    """

    template_name = "views/evidence_detail.jinja"

    PARAM_COLLAPSED = "collapsed"

    def get(self, request, *args, **kwargs):
        self.entry = self._get_entry(kwargs["notion_id"])
        return super().get(request, *args, **kwargs)

    def get_template_names(self) -> list:
        if not self.request.headers.get("HX-Request"):
            return [self.template_name]

        if self.PARAM_COLLAPSED in self.request.GET:
            return ["_partials/evidence_card.jinja"]

        return ["_partials/evidence_card_expanded.jinja"]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["entry"] = self.entry
        ctx["page"] = self
        ctx["listing_page"] = self.listing_page
        # The listing's filters, carried on the request that opens a record so a
        # topic tag inside it still knows what the reader had chosen. Empty for
        # a reader who arrived at the record on its own.
        ctx["evidence_query"] = evidence.parse(self.request.GET)
        ctx["meta_title"] = self.title
        ctx["meta_description"] = self.entry.display_summary
        global_context(ctx)  # Adds in nav settings etc.
        return ctx

    @cached_property
    def title(self) -> str:
        """Records have no title field, so the one sentence description stands
        in for one. Open Ownership may add a real title later.
        """
        return self.entry.description

    @cached_property
    def listing_page(self):
        """The Evidence Centre, for the breadcrumb and the close link.

        There is only ever one, but it is an editable page, so its URL cannot be
        hard coded here.
        """
        page = BotCentrePage.objects.live().filter(locale=Locale.get_active()).first()
        if not page:
            page = BotCentrePage.objects.live().first()
        return page

    @cached_property
    def breadcrumb_page(self):
        return self.listing_page

    def _get_entry(self, notion_id: str):
        """Only records cleared for publication have a page.

        `publishable` is the same gate the listing uses, so a record can never
        be missing from the listing but reachable by URL.
        """
        return get_object_or_404(
            ImpactEntry.objects.publishable().prefetch_related(*evidence.PREFETCH),
            notion_id=notion_id,
        )


class EvidenceExportView(View):
    """The evidence records as CSV.

    The same query parameters as the listing, so the download matches whatever
    the reader was looking at. No parameters means the whole dataset. The result
    set is never paginated: an export is the lot, not the page they were on.

    Only the columns Open Ownership cleared for publication are written. The
    tracker's internal columns are synced but must not leave the site.
    """

    COLUMNS = (
        "Description",
        "Summary",
        "Year",
        "Jurisdiction",
        "Region",
        "Topic",
        # "Type",  # Disable "Type"
        "Type of resource",
        "Source",
        "Record URL",
    )

    def get(self, request, *args, **kwargs):  # noqa: ARG002
        response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{self._filename(request)}"'},
        )
        root_url = self._root_url(request)
        writer = csv.writer(response)
        writer.writerow(self.COLUMNS)
        for entry in evidence.all_records(request.GET):
            writer.writerow(self._row(root_url, entry))
        return response

    def _row(self, root_url: str, entry) -> list:
        """One record, in the order `COLUMNS` names."""
        return [
            entry.description,
            entry.summary,
            entry.year or "",
            entry.display_jurisdictions,
            entry.display_region_names,
            entry.display_topics,
            # entry.display_data_users,  # Disable "Type"
            entry.display_resource_types,
            entry.source_url,
            f"{root_url}{entry.get_absolute_url()}",
        ]

    def _root_url(self, request) -> str:
        """What to put in front of a record's path.

        A CSV is read away from the site, so the record URL has to be absolute.
        Wagtail's site record is used rather than `build_absolute_uri` because it
        gives the site's canonical address rather than whichever hostname the
        reader happened to arrive on, and this file is one Open Ownership may
        hand out.
        """
        site = Site.find_for_request(request) or Site.objects.filter(is_default_site=True).first()
        if site:
            return site.root_url.rstrip("/")
        return settings.BASE_URL.rstrip("/")

    def _filename(self, request) -> str:
        """Named for what it holds, so two downloads do not collide on disk."""
        if evidence.parse(request.GET).is_narrowed:
            return "bot-evidence-filtered.csv"
        return "bot-evidence.csv"
