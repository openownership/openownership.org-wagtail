from django.db.models.aggregates import Count
from django.http import Http404
from django.shortcuts import reverse
from django.views.generic import TemplateView
from wagtail.core.models import Locale, Page, Site

from modules.core.utils import get_site_context
from modules.core.views import PaginatedListView
from modules.content.models import content_page_models, PressLink
from .models import BaseTag, Category, DummyPage, FocusAreaTag, SectorTag, PublicationType


####################################################################################
# Mixins

class TaxonomyMixin:
    """
    Mixin for the pages that display taxonomies AND pages tagged by taxonomies.

    Provides the common things needed by both, such as:

    * Setting self.section_page based on section_slug in the URL
    * Setting context data needed to make it behave more like a Wagtail Page
    * Setting menu_pages (which child classes could override)
    """

    # Will be a Page, which listed Pages will be descendants of.
    section_page = None

    taxonomy_class = None

    def get(self, request, *args, **kwargs):
        section_slug = kwargs.pop('section_slug')
        self.section_page = self._get_section_page(section_slug)

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        site = self._get_site()

        context.update(
            **get_site_context(site),
        )

        context['meta_title'] = self.title

        # So that templates looking for a Page object don't error:
        context['page'] = self

        context['menu_pages'] = self._get_menu_pages()

        return context

    @property
    def title(self):
        "To mimic a Page object"
        return "<no title set>"

    def _get_menu_pages(self):
        """
        Returns the data needed for menu_pages for the left-hand menu in the template.
        """

        # 1. Start off with the parent section page.

        menu_pages = [{"page": self.section_page, "children": []}]

        # 2. Add an entry for each kind of tag.
        # If it's the same as what we're viewing, include each sibling tag.

        taxonomy_classes = [FocusAreaTag, SectorTag, PublicationType]
        section_slug = self.section_page.slug

        for taxonomy_class in taxonomy_classes:
            # Make a dummy page for the taxonomy itself, top level of menu:
            p = DummyPage()
            p.title = taxonomy_class._meta.verbose_name
            p.pk = f"TaxonomyView-{section_slug}-{taxonomy_class.__name__}"
            p.url = reverse(
                'taxonomy',
                kwargs={
                    'section_slug': section_slug,
                    'taxonomy_slug': taxonomy_class.url_slug
                }
            )
            menu_item = {"page": p, "children": []}

            # Tags that could appear beneath, second level of menu:
            tags_with_pages = self._get_tags_that_have_pages(taxonomy_class)

            if len(tags_with_pages) > 0:
                # Whether we're viewing this taxonomy or not, it has tags with pages,
                # so we'll show a link to it.
                if taxonomy_class == self.taxonomy_class:
                    # We're viewing this taxonomy, so add the tags as children.
                    for tag in tags_with_pages:
                        # Make a dummy page to fool the template:
                        t = DummyPage()
                        t.pk = f"TaxonomyPagesView-{section_slug}-{taxonomy_class.__name__}-{tag.slug}"
                        t.title = tag.name
                        t.url = tag.get_url(section_slug)
                        menu_item["children"].append(t)

                menu_pages.append(menu_item)

        # 3. Add the "Latest" link, if there are any

        latest_count = (
            self.section_page.get_descendants()
            .live().public()
            .exact_type(*content_page_models)
            .filter(locale=Locale.get_active())
        ).count()
        if latest_count > 0:
            p = DummyPage()
            p.title = f'Latest {self.section_page.title}'
            p.pk = f"SectionLatestPagesView-{section_slug}"
            p.url = reverse('section-latest-pages', kwargs={'section_slug': section_slug})
            menu_pages.append({"page": p, "children": []})

        # 4. Add the "Press links" link, if there are any

        press_link_count = PressLink.objects.filter(section_page=self.section_page).count()
        if press_link_count > 0:
            p = DummyPage()
            p.title = 'Press links'
            p.pk = f"SectionPressLinksView-{section_slug}"
            p.url = reverse('section-press-links', kwargs={'section_slug': section_slug})
            menu_pages.append({"page": p, "children": []})

        return menu_pages

    def _get_tags_that_have_pages(self, taxonomy_class):
        """
        Returns all the tags/categories of taxonomy_class, but only ones containing live Pages.

        The Pageas must be live, and within this section and Locale.

        Each object will also have a count element with the number of Pages it
        contains.

        taxonomy_class is like SectorTag, FocusAreaTag, PublicationType
        """

        objects = []

        if issubclass(taxonomy_class, BaseTag):

            # All the live pages in this section and locale:
            page_ids = (
                Page.objects.live().public()
                .descendant_of(self.section_page)
                .filter(locale=Locale.get_active())
                .values_list("id", flat=True)
            )

            # How to get the tags that are used on pages with these IDs:
            tag_filter = {
                f'{taxonomy_class.related_pages_name}__content_object_id__in': page_ids
            }

            objects = (
                taxonomy_class.objects.filter(**tag_filter)
                .annotate(count=Count(taxonomy_class.related_pages_name))
            )

        elif issubclass(taxonomy_class, Category):

            for cat in taxonomy_class.objects.all():
                # Assumes that cat.pages already filters for section and Locale:
                cat.count = cat.pages.descendant_of(self.section_page).count()
                if cat.count > 0:
                    objects.append(cat)

        return objects

    def _get_site(self):
        return Site.find_for_request(self.request)

    def _get_section_page(self, slug):
        "Which section Page is this page within?"
        try:
            page = (
                Page.objects.live().public()
                .filter(locale=Locale.get_active())
                .get(slug=slug)
            )
        except Page.DoesNotExist:
            raise Http404
        else:
            return page


####################################################################################
# Parent classes


class TaxonomyPagesView(TaxonomyMixin, PaginatedListView):
    """Parent class for displaying a list of Pages by some kind of taxonomy, within a section.

    Child classes must define:

    taxonomy_class - a child of BaseTag. The tag we're filtering pages on.
    _get_tags_that_have_pages() - a method. See its comments for description.

    From the URL it expects:

    * section_slug - the slug of a Page that is an ancestor of all the Pages to list.
    * tag_slug - the slug of the taxonomy_class that's used to find all the Pages to list.
    """

    # Child classes must set this:
    taxonomy_class = None

    template_name = 'taxonomy/taxonomy_pages.jinja'

    # Will be an object, a child of BaseTag:
    tag = None

    def __init__(self, *args, **kwargs):
        if self.taxonomy_class is None:
            raise NotImplementedError(
                f'{self.__class__.__name__} should have taxonomy_class defined '
                f'but it is "{self.taxonomy_class}".'
            )
        return super().__init__(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        """Set self.section_page and self.tag before anything else.
        If we can't, it 404s.
        """
        tag_slug = kwargs.pop('tag_slug')
        self.tag = self._get_tag(tag_slug)

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['tag'] = self.tag

        return context

    def get_queryset(self):
        "Override in child classes"
        return []

    @property
    def title(self):
        "To mimic a Page object"
        return self.tag.name

    @property
    def pk(self):
        "To mimic a Page object"
        return (
            f"TaxonomyPagesView-{self.section_page.slug}-{self.taxonomy_class.__name__}-"
            f"{self.tag.slug}"
        )

    def _get_tag(self, slug):
        try:
            tag = self.taxonomy_class.objects.get(slug=slug)
        except self.taxonomy_class.DoesNotExist:
            raise Http404
        else:
            return tag


class TagPagesView(TaxonomyPagesView):
    """
    Parent class for displaying a list of Pages by some kind of Tag, within a section.

    Child classes must define:

    taxonomy_class - a child of BaseTag. The tag we're filtering pages on.
    """

    def get_queryset(self):
        related_pages = getattr(self.tag, self.taxonomy_class.related_pages_name)
        page_ids = related_pages.values_list('content_object__id', flat=True)

        pages = (
            Page.objects.live().public()
            .descendant_of(self.section_page).specific()
            .filter(locale=Locale.get_active())
            .filter(id__in=page_ids)
            .order_by('-first_published_at')
        )

        return pages


class CategoryPagesView(TaxonomyPagesView):
    """
    Parent class for displaying a list of Pages by some kid of Category, within a section.

    Child classes must define:

    taxonomy_class - a child of BaseTag. The tag we're filtering pages on.
    """

    def get_queryset(self):
        return self.tag.pages.descendant_of(self.section_page)


####################################################################################
# The actual classes for viewing specific taxonomies.


class SectorPagesView(TagPagesView):
    """
    Viewing all Pages tagged with a SectorTag that are descended from a SectionPage.
    """

    taxonomy_class = SectorTag


class FocusAreaPagesView(TagPagesView):
    """
    Viewing all Pages tagged with an AreaOfFocusTag that are descended from a SectionPage.
    """

    taxonomy_class = FocusAreaTag


class PublicationTypePagesView(CategoryPagesView):
    """
    Viewing all Pages of a PublicationType that are descended from a SectionPage.
    """

    taxonomy_class = PublicationType


####################################################################################
#  Other views

class TaxonomyView(TaxonomyMixin, TemplateView):
    """
    For viewing a taxonomy itself, with links to all of the tags/categories within it.
    e.g. For viewing "Sector" and showing links to "Banking", "Technology", etc.
    """
    template_name = 'taxonomy/taxonomy_detail.jinja'

    # Will be set based on taxonomy_slug in the URL:
    taxonomy_class = None

    def get(self, request, *args, **kwargs):
        taxonomy_slug = kwargs.pop('taxonomy_slug')
        self.taxonomy_class = self._get_taxonomy_class(taxonomy_slug)

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        site = self._get_site()

        context.update(
            **get_site_context(site),
        )

        context['meta_title'] = self.taxonomy_class._meta.verbose_name

        # So that templates looking for a Page object don't error:
        context['page'] = self

        context['pages'] = self._get_pages()

        return context

    @property
    def title(self):
        "To mimic a Page object"
        return self.taxonomy_class._meta.verbose_name

    @property
    def pk(self):
        "To mimic a Page object"
        return (
            f"TaxonomyView-{self.section_page.slug}-{self.taxonomy_class.__name__}"
        )

    def _get_pages(self):
        """
        Get the Pages that we'll display in the main page content.
        """
        pages = []

        tags = self._get_tags_that_have_pages(self.taxonomy_class)

        for tag in tags:
            pages.append(tag.to_dummy_page(self.section_page.slug))

        return pages

    def _get_taxonomy_class(self, slug):
        """
        Return the taxonomy class based on the slug, or else 404.
        """
        if slug == 'focus-areas':
            return FocusAreaTag
        elif slug == 'sectors':
            return SectorTag
        elif slug == 'types':
            return PublicationType
        else:
            raise Http404


class SectionLatestPagesView(TaxonomyMixin, PaginatedListView):
    """
    Viewing the latest content within a section. No tags.

    But we inherit from TaxonomyMixin so we can use its stuff for
    generating menu_pages and pretending to be a real Wagtail Page.
    """
    template_name = 'taxonomy/pages.jinja'

    @property
    def title(self):
        "To mimic a Page object"
        return f"Latest {self.section_page.title}"

    @property
    def pk(self):
        "To mimic a Page object"
        return (f"SectionLatestPagesView-{self.section_page.slug}")

    def get_queryset(self):
        return (
            self.section_page.get_descendants()
            .live().public()
            .exact_type(*content_page_models)
            .filter(locale=Locale.get_active())
            .specific()
            .order_by('-first_published_at')
        )


class SectionPressLinksView(TaxonomyMixin, PaginatedListView):
    """
    Viewing all the Press Link snippets within this section. No tags.

    But we inherit from TaxonomyMixin so we can use its stuff for
    generating menu_pages and pretending to be a real Wagtail Page.
    """
    template_name = 'taxonomy/press_links.jinja'

    @property
    def title(self):
        "To mimic a Page object"
        return "Press links"

    @property
    def pk(self):
        "To mimic a Page object"
        return (f"SectionPressLinksView-{self.section_page.slug}")

    def get_queryset(self):
        return (
            PressLink.objects.filter(section_page=self.section_page)
            .order_by("-first_published_at")
        )
