from django.http import Http404
from django.urls import reverse
from wagtail.core.models import Locale, Page, Site

from modules.core.utils import get_site_context
from modules.core.views import PaginatedListView
from .models import FocusAreaTag, SectorTag


class DummyPage(object):
    pk = None
    title = ""
    url = ""


class TaggedView(PaginatedListView):
    """Parent class for displaying a list of Pages by some kind of tag, within a section.

    Child classes must define:

    tag_class - a child of BaseTag. The tag we're filtering pages on.
    tag_related_pages_name - the related_name argument used by the associated
        child of ItemBase that's linked to the tag_class

    From the URL it expects:

    * section_slug - the slug of a Page that is an ancestor of all the Pages to list.
    * tag_slug - the slug of the tag_class that's used to find all the Pages to list.
    """

    # Child classes must set these two:
    tag_class = None
    tag_related_pages_name = None

    template_name = 'taxonomy/tagged.jinja'

    # Will be an object, a child of BaseTag:
    tag = None

    # Will be a Page, which listed Pages will be descendants of.
    section_page = None

    def __init__(self, *args, **kwargs):
        if self.tag_class is None or self.tag_related_pages_name is None:
            raise NotImplementedError(
                f'{self.__class__.__name__} should have both tag_class and '
                f'tag_related_pages_name defined but they are "{self.tag_class}" and "'
                f'{self.tag_related_pages_name}"'
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
        ids = related_pages.values_list('content_object__id', flat=True)

        pages = (
            Page.objects.live().public()
            .descendant_of(self.section_page).specific()
            .filter(locale=Locale.get_active())
            .filter(id__in=ids)
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
            f"TaggedView-{self.section_page.slug}-{self.tag_class.__name__}-"
            f"{self.tag.slug}"
        )

    def _get_menu_pages(self):

        # 1. Start off with the parent section page.

        menu_pages = [{"page": self.section_page, "children": []}]

        # 2. Add an entry for each kind of tag.
        # If it's the same as what we're viewing, include each sibling tag.

        tag_classes = [
            # Mapping class name to URL name:
            (FocusAreaTag, "focusarea-tag"),
            (SectorTag, "sector-tag"),
        ]
        section_slug = self.section_page.slug

        for tag_class, url_name in tag_classes:
            p = DummyPage()
            p.title = tag_class._meta.verbose_name
            p.pk = f"TaggedView-{section_slug}-{tag_class.__name__}"
            menu_item = {"page": p, "children": []}

            if tag_class == self.tag_class:
                # Add all the sibling tags to this current one.
                for tag in self.tag_class.objects.all():
                    # Make a dummy page to fool the template:
                    t = DummyPage()
                    t.pk = f"TaggedView-{section_slug}-{tag_class.__name__}-{tag.slug}"
                    t.title = tag.name
                    t.url = reverse(
                        url_name,
                        kwargs={"section_slug": section_slug, "tag_slug": tag.slug}
                    )
                    menu_item["children"].append(t)

            menu_pages.append(menu_item)

        return menu_pages


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


class SectorView(TaggedView):

    tag_class = SectorTag

    tag_related_pages_name = "sector_related_pages"


class FocusAreaView(TaggedView):

    tag_class = FocusAreaTag

    tag_related_pages_name = "focusarea_related_pages"
