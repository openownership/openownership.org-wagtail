from django.db.models.aggregates import Count
from django.http import Http404
from wagtail.core.models import Locale, Page, Site

from modules.core.utils import get_site_context
from modules.core.views import PaginatedListView
from modules.content.models import BlogArticlePage, JobPage, NewsArticlePage, PublicationFrontPage
from .models import DummyPage, FocusAreaTag, SectorTag, PublicationType




class TaxonomyView(PaginatedListView):
    """Parent class for displaying a list of Pages by some kind of taxonomy, within a section.

    Child classes must define:

    tag_class - a child of BaseTag. The tag we're filtering pages on.
    _get_tags_that_have_pages() - a method. See its comments for description.

    From the URL it expects:

    * section_slug - the slug of a Page that is an ancestor of all the Pages to list.
    * tag_slug - the slug of the tag_class that's used to find all the Pages to list.
    """

    # Child classes must set this:
    tag_class = None

    template_name = 'taxonomy/tagged.jinja'

    # Will be an object, a child of BaseTag:
    tag = None

    # Will be a Page, which listed Pages will be descendants of.
    section_page = None

    def __init__(self, *args, **kwargs):
        if self.tag_class is None:
            raise NotImplementedError(
                f'{self.__class__.__name__} should have tag_class defined '
                f'but it is "{self.tag_class}".'
            )
        return super().__init__(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        """Set self.section_page and self.tag before anything else.
        If we can't, it 404s.
        """
        section_slug = kwargs.pop('section_slug')
        self.section_page = self._get_section_page(section_slug)

        tag_slug = kwargs.pop('tag_slug')
        self.tag = self._get_tag(tag_slug)

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        site = self._get_site()

        context.update(
            **get_site_context(site),
        )

        context['tag'] = self.tag
        context['meta_title'] = self.tag.name

        # So that templates looking for a Page object don't error:
        context['page'] = self

        context['menu_pages'] = self._get_menu_pages()

        return context

    def get_queryset(self):
        related_pages = getattr(self.tag, self.tag_related_pages_name)
        page_ids = related_pages.values_list('content_object__id', flat=True)

        pages = (
            Page.objects.live().public()
            .descendant_of(self.section_page).specific()
            .filter(locale=Locale.get_active())
            .filter(id__in=page_ids)
            .order_by('-first_published_at')
        )

        return pages

    @property
    def title(self):
        "To mimic a Page object"
        return self.tag.name

    @property
    def pk(self):
        "To mimic a Page object"
        return (
            f"TaxonomyView-{self.section_page.slug}-{self.tag_class.__name__}-"
            f"{self.tag.slug}"
        )

    def _get_menu_pages(self):

        # 1. Start off with the parent section page.

        menu_pages = [{"page": self.section_page, "children": []}]

        # 2. Add an entry for each kind of tag.
        # If it's the same as what we're viewing, include each sibling tag.

        tag_classes = [FocusAreaTag, SectorTag, PublicationType]
        section_slug = self.section_page.slug

        for tag_class in tag_classes:
            p = DummyPage()
            p.title = tag_class._meta.verbose_name
            p.pk = f"TaxonomyView-{section_slug}-{tag_class.__name__}"
            menu_item = {"page": p, "children": []}

            if tag_class == self.tag_class:
                # Add all the sibling tags to this current one.
                for tag in self._get_tags_that_have_pages(tag_class):
                    # Make a dummy page to fool the template:
                    t = DummyPage()
                    t.pk = f"TaxonomyView-{section_slug}-{tag_class.__name__}-{tag.slug}"
                    t.title = tag.name
                    t.url = tag.get_url(section_slug)
                    menu_item["children"].append(t)

            menu_pages.append(menu_item)

        return menu_pages

    def _get_tags_that_have_pages(self, tag_class):
        """
        Child classes should define this.

        It should return a list/queryset of Tag/Category objects.

        It should not include any that haven't been used on any Pages.

        Each one should have a count property, of the number of live Pages within
        this section and Locale that are tagged with that Tag/Category.
        """
        raise NotImplementedError(
            f'{self.__class__.__name__} should have a _get_tags_that_have_pages() method '
            'defined but it does not.'
        )

    def _get_site(self):
        return Site.find_for_request(self.request)

    def _get_section_page(self, slug):
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

    def _get_tag(self, slug):
        try:
            tag = self.tag_class.objects.get(slug=slug)
        except self.tag_class.DoesNotExist:
            raise Http404
        else:
            return tag


class TagView(TaxonomyView):
    """
    Parent class for displaying a list of Pages by some kind of Tag, within a section.

    Child classes must define:

    tag_class - a child of BaseTag. The tag we're filtering pages on.
    tag_related_pages_name - the related_name argument used by the associated
        child of ItemBase that's linked to the tag_class
    """

    # Child classes must set this:
    tag_related_pages_name = None

    def __init__(self, *args, **kwargs):
        if self.tag_related_pages_name is None:
            raise NotImplementedError(
                f'{self.__class__.__name__} should have tag_related_pages_name defined '
                f'but it is "{self.tag_related_pages_name}".'
            )
        return super().__init__(*args, **kwargs)

    def _get_tags_that_have_pages(self, tag_class):
        """
        Returns all the tags of tag_class, but only ones containing live Pages.
        The Pageas must be live, and within this section.
        Each tag object will also have a count element with the number of Pages it
        contains.

        tag_class is like SectorTag or FocusAreaTag
        """
        page_ids = (
            Page.objects.live().public()
            .descendant_of(self.section_page)
            .filter(locale=Locale.get_active())
            .values_list("id", flat=True)
        )

        tag_filter = {f'{self.tag_related_pages_name}__content_object_id__in': page_ids}

        return (
            tag_class.objects.filter(**tag_filter)
            .annotate(count=Count(self.tag_related_pages_name))
        )


class CategoryView(TaxonomyView):
    """
    Parent class for displaying a list of Pages by some kid of Category, within a section.

    Child classes must define:

    tag_class - a child of BaseTag. The tag we're filtering pages on.
    """

    def get_queryset(self):
        return self.tag.pages.descendant_of(self.section_page)

    def _get_tags_that_have_pages(self, tag_class):
        """
        Returns a list of all the Categories of this class that have live pages
        in this section and Locale.

        Assumes that tag_class has a pages property that filters for live(), and locale.

        I doubt this is efficient but...
        """
        categories = []

        for cat in tag_class.objects.all():
            cat.count = cat.pages.descendant_of(self.section_page).count()
            if cat.count > 0:
                categories.append(cat)

        return categories


####################################################################################
# The actual classes for specific taxonomies.


class SectorView(TagView):
    """
    Viewing all Pages tagged with a SectorTag that are descended from a SectionPage.
    """

    tag_class = SectorTag

    tag_related_pages_name = "sector_related_pages"


class FocusAreaView(TagView):
    """
    Viewing all Pages tagged with an AreaOfFocusTag that are descended from a SectionPage.
    """

    tag_class = FocusAreaTag

    tag_related_pages_name = "focusarea_related_pages"


class PublicationTypeView(CategoryView):
    """
    Viewing all Pages of a PublicationType that are descended from a SectionPage.
    """

    tag_class = PublicationType
