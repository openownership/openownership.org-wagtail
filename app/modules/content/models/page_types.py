"""
    content.models.pages_types
    ~~~~~~~~~~~~~~~~~~~~~~~
    Core page types. Extend these to create the actual page models.

    ie: class ArticlePage(ContentPageType):
        [...]
"""

# 3rd party
from consoler import console
from django.apps import apps
from django.db import models
from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger
from django.utils.functional import cached_property
from django.utils.html import strip_tags
from jinja2.filters import do_truncate
from django.utils.translation import gettext_lazy as _

from wagtail.admin.edit_handlers import FieldPanel, ObjectList, TabbedInterface, StreamFieldPanel
from wagtail.core import fields
from wagtail.core.models import Locale, Page
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index
from wagtail.utils.decorators import cached_classmethod

from wagtailcache.cache import WagtailCacheMixin

# Project
from django.core.paginator import Paginator
from modules.core.utils import get_site_context
from modules.content.blocks import (
    landing_page_blocks, article_page_body_blocks, additional_content_blocks
)


####################################################################################################
# Core / general page types
####################################################################################################

class BasePage(WagtailCacheMixin, Page):

    class Meta:
        abstract = True

    thumbnail = models.ForeignKey(
        settings.IMAGE_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    blurb = models.TextField(
        blank=True,
        null=True
    )

    display_date = models.DateField(
        blank=True,
        null=True,
        help_text=_("If blank, this will be set to the date the page was first published")
    )

    content_panels = Page.content_panels

    promote_panels = [
        ImageChooserPanel('thumbnail'),
        FieldPanel('blurb'),
    ] + Page.promote_panels

    settings_panels = [
        FieldPanel('display_date'),
    ] + Page.settings_panels

    search_fields = Page.search_fields + [
        index.SearchField('blurb'),
        index.SearchField('search_description'),
    ]

    @cached_property
    def translations(self):
        result = []
        try:
            translations = self.get_translations().public().live()
            for page in translations:
                if not page.alias_of:  # If the page is just a mirror, alias_of returns the source
                    result.append({
                        'language': page.locale.get_display_name(),
                        'url': page.url
                    })
        except Exception as e:
            console.warn(e)
        else:
            return result

    @cached_property
    def breadcrumbs(self):
        ancestors = self.\
            get_ancestors()\
            .exclude(slug__in=['root', 'home'])\
            .values('title', 'url_path')
        breadcrumbs = []
        for page in ancestors:
            url = page.get('url_path', '').replace('/home', '', 1)
            breadcrumbs.append({'url': url, 'title': page.get('title')})
        return breadcrumbs

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        site = self.get_site()

        context.update(
            **get_site_context(site),
        )
        context.update(
            **self.get_metadata_settings(site)
        )

        context['meta_description'] = self.page_meta_description

        return context

    @cached_classmethod
    def get_admin_tabs(cls):
        tabs = [
            (cls.content_panels, _('Content')),
            (cls.promote_panels, _('Promote')),
            (cls.settings_panels, _('Settings')),
        ]
        return tabs

    @cached_classmethod
    def get_edit_handler(cls):  # NOQA

        tabs = cls.get_admin_tabs()

        edit_handler = TabbedInterface([
            ObjectList(tab[0], heading=tab[1]) for tab in tabs
        ])

        return edit_handler.bind_to(model=cls)

    def get_meta_title(self):
        if self.seo_title:
            return self.seo_title
        else:
            return self.title

    @cached_property
    def page_meta_description(self):
        if self.search_description:
            return self.search_description

        if getattr(self, 'blurb', False):
            return self.blurb

        if hasattr(self, 'body'):
            try:
                for block in self.body.get_prep_value():
                    if block['type'] == 'rich_text':
                        txt = strip_tags(block['value'])
                        return do_truncate({}, txt, 200, leeway=5)
            except Exception:
                site_settings = self.get_metadata_settings()
                return site_settings['meta_description']

        site_settings = self.get_metadata_settings()
        return site_settings['meta_description']

    def get_metadata_settings(self, site=None):
        from modules.settings.models import SiteSettings

        if not site:
            site = self.get_site()

        default_meta = SiteSettings.get_metatag_context(site)
        title = self.get_meta_title() or default_meta.get('meta_title')
        description = default_meta.get('meta_description')
        image = self.thumbnail or default_meta.get('meta_image')

        return {
            'meta_title': title,
            'meta_description': description,
            'meta_image': image
        }

    @cached_property
    def human_display_date(self):
        if self.display_date:
            return self.display_date.strftime('%d %B %Y')

    @cached_property
    def page_type(self):
        return str(self.__class__.__name__)

    @cached_property
    def all_pks(self):
        """
        Returns a list of IDs of this Page and all its translated versions, if any.
        """
        return [self.pk] + [p.pk for p in self.get_translations()]

    @cached_property
    def section_page(cls):
        """Get the top-level page this page is within, or *is*.
        e.g. About, Research, Implmentation, etc.

        e.g. a page that's a child or grandchild of "Research" will return "Research" page.

        But the "Research" page will return itself.

        Ignores root and home when calculating "top-level page".
        """
        ancestors = cls.get_ancestors()
        if len(ancestors) == 2:
            # Top-level section page itself.
            return cls
        elif len(ancestors) > 2:
            return ancestors[2]
        else:
            return None

    @cached_property
    def breadcrumb_page(cls):
        """For pages that have a 'Back to ...' breadcrumb link, returns the page to
        go 'back' to. For most it's the parent, but some require going a bit higher;
        they can override this method.
        """
        return cls.get_parent()

    @property
    def show_display_date_on_card(self):
        "Whether to show the date when displaying a card about this page."
        return False

    @property
    def show_display_date_on_page(self):
        """Whether to show the date when displaying the page.
        (Assuming it uses a template that uses it.)
        """
        return True

    @cached_property
    def card_blurb(self):
        "So that other types of page can display different fields in place of blurb on cards"
        return self.blurb


####################################################################################################
# Landing Page Type
####################################################################################################


class LandingPageType(BasePage):
    """
    A landing page is a curated content page meant as a jumping off point to lead users deeper
    into the content. It would typically be thematic.
    """

    class Meta:
        abstract = True

    body = fields.StreamField(landing_page_blocks, blank=True)

    model_content_panels = [
        StreamFieldPanel('body')
    ]

    content_panels = BasePage.content_panels + model_content_panels

    search_fields = BasePage.search_fields + [
        index.SearchField('body')
    ]

    def get_context(self, request, *args, **kwargs) -> dict:
        context = super().get_context(request, *args, **kwargs)
        context['body_classes'] = 'landing-page'
        return context


####################################################################################################
# Content Page Type
####################################################################################################

class ContentPageType(BasePage):
    """
    Typically used for articles, news posts, news etc.
    """

    class Meta:
        abstract = True

    template = 'content/article_page.jinja'

    body = fields.StreamField(article_page_body_blocks, blank=True)
    additional_content = fields.StreamField(additional_content_blocks, blank=True)

    model_content_panels = [
        StreamFieldPanel('body'),
        StreamFieldPanel('additional_content'),
    ]

    content_panels = BasePage.content_panels + model_content_panels

    search_fields = BasePage.search_fields + [
        index.SearchField('body'),
    ]

    @property
    def date(self):
        return self.display_date

    @property
    def display_title(self):
        "Allows us to override it for special cases"
        return self.title

    @property
    def show_display_date_on_card(self):
        "Whether to show the date when displaying a card about this page."
        return True


####################################################################################################
# Index Page Type
####################################################################################################

class IndexPageType(BasePage):

    class Meta:
        abstract = True

    objects_model = None

    objects_per_page = 10

    intro = fields.RichTextField(
        blank=True, null=True, features=settings.RICHTEXT_INLINE_FEATURES,
    )

    content_panels = BasePage.content_panels + [
        FieldPanel('intro')
        # StreamFieldPanel('child_page_stream')
    ]

    def get_objects_model(self):
        if type(self.objects_model) is str:
            return apps.get_model(self.objects_model)

        return self.objects_model

    def get_order_by(self):
        return ['-display_date', '-last_published_at']

    def base_queryset(self):
        return (
            self.get_objects_model()
            .objects
            .live().public().filter(locale=Locale.get_active())
            .select_related('thumbnail')
        )

    def get_queryset(self, request):

        """
        This returns the queryset needed to paginate the objects on the page. It pulls all the
        valid filters from get_filter_options and carries out the respective logic on the queryset.
        """
        query = self.base_queryset().distinct()

        try:
            pages = sorted(query, key=lambda x: x.display_date, reverse=True)
        except Exception as e:
            console.warn(e)
            return query.order_by('-first_published_at')
        else:
            return pages

    def paginate_objects(self, request):
        queryset = self.get_queryset(request)

        paginator = Paginator(queryset, self.objects_per_page)
        current_page = request.GET.get('page', 1)
        try:
            return paginator.page(current_page)
        except PageNotAnInteger:
            return paginator.page(1)
        except EmptyPage:
            return paginator.page(paginator.num_pages)

    def get_context(self, request, *args, **kwargs) -> dict:
        ctx = super().get_context(request, *args, **kwargs)

        query_string = request.GET.copy()
        pagination_params = query_string.pop('page', None) and query_string.urlencode()

        ctx.update({
            'page_obj': self.paginate_objects(request),
            'pagination_params': pagination_params
        })

        return ctx

    @classmethod
    def can_create_at(cls, parent) -> bool:
        return super().can_create_at(parent) and not cls.objects.exists()
