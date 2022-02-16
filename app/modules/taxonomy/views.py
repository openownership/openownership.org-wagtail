from django.http import Http404
from wagtail.core.models import Page, Site

from modules.core.utils import get_site_context
from modules.core.views import PaginatedListView
from .models import FocusAreaTag, SectorTag


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

        return context

    def get_queryset(self):
        related_pages = getattr(self.tag, self.tag_related_pages_name)
        ids = related_pages.values_list('content_object__id', flat=True)

        pages = (
            Page.objects.live().public()
            .descendant_of(self.section_page)
            .filter(id__in=ids)
            .order_by('-first_published_at')
        )

        return pages

    def _get_site(self):
        return Site.find_for_request(self.request)

    def _get_section_page(self, slug):
        try:
            page = Page.objects.live().public().get(slug=slug)
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
