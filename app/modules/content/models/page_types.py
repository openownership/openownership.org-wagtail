"""
    content.models.pages_types
    ~~~~~~~~~~~~~~~~~~~~~~~
    Core page types. Extend these to create the actual page models.

    ie: class ArticlePage(ContentPageType):
        [...]
"""

# 3rd party
from django.db import models
from django.conf import settings
from wagtail.core import fields
from wagtail.search import index
from django.utils.html import strip_tags
from django.utils.text import slugify
from wagtailcache.cache import WagtailCacheMixin
from wagtail.core.models import Page
from django.utils.functional import cached_property
from wagtail.utils.decorators import cached_classmethod
from wagtail.admin.edit_handlers import FieldPanel, ObjectList, TabbedInterface, StreamFieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel

# Project
from modules.content.blocks import (
    landing_page_blocks, article_page_body_blocks, contents_page_body_blocks,
    additional_content_blocks
)

from modules.content.models.mixins import PageHeroMixin


####################################################################################################
# Core / general page types
####################################################################################################

class BasePage(WagtailCacheMixin, PageHeroMixin, Page):

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
        help_text="If blank, this will be set to the date the page was first published"
    )

    # Panels
    content_panels = Page.content_panels
    thumbnail_panels = PageHeroMixin.hero_panels + [
        ImageChooserPanel('thumbnail'),
        FieldPanel('blurb'),
    ]

    promote_panels = Page.promote_panels

    settings_panels = [
        FieldPanel('display_date'),
    ] + Page.settings_panels

    search_fields = Page.search_fields + [
        index.SearchField('blurb'),
        index.SearchField('search_description'),
    ]

    @cached_classmethod
    def get_admin_tabs(cls):
        tabs = [
            (cls.content_panels, 'Content'),
            (cls.thumbnail_panels, 'Thumbnail'),
            (cls.promote_panels, 'Promote'),
            (cls.settings_panels, 'Settings'),
        ]
        return tabs

    @cached_classmethod
    def get_edit_handler(cls):  # NOQA

        tabs = cls.get_admin_tabs()

        edit_handler = TabbedInterface([
            ObjectList(tab[0], heading=tab[1], classname=slugify(tab[1])) for tab in tabs
        ])

        return edit_handler.bind_to(model=cls)

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context.update(**BasePage.get_site_settings(self))

        context.update({
            'site_name': settings.SITE_NAME
        })

        return context

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

    @classmethod
    def get_site_settings(cls, page):
        from modules.core.models import (
            SocialMediaSettings, AnalyticsSettings, NavigationSettings,
            UpdateBannerSettings
        )

        site = page.get_site()
        context = {}

        context.update(
            **NavigationSettings.get_for_context(site),
            **SocialMediaSettings.get_for_context(site),
            **AnalyticsSettings.get_for_context(site),
            **UpdateBannerSettings.get_for_context(site, page),
            **cls.get_metadata_settings(page)
        )
        return context

    def get_meta_title(self):
        if self.seo_title:
            return self.seo_title
        else:
            return self.title

    def get_meta_description(self):
        if self.search_description:
            return self.search_description
        if getattr(self, 'blurb', False):
            return self.blurb
        try:
            for _ in self.body.stream_data:
                if _['type'] == 'rich_text':
                    return strip_tags(_['value'])
        except Exception:
            pass
        return None

    def get_metadata_settings(self):
        from modules.core.models import (
            MetaTagSettings
        )

        site = self.get_site()
        default_meta = MetaTagSettings.get_for_context(site)
        title = self.get_meta_title() or default_meta.get('meta_title')
        description = self.get_meta_description() or default_meta.get('meta_description')
        image = self.thumbnail or default_meta.get('meta_image')

        return {
            'meta_title': title,
            'meta_description': description,
            'meta_image': image
        }

    @cached_property
    def page_type(self):
        return str(self.__class__.__name__)


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

    content_panels = BasePage.content_panels + [
        StreamFieldPanel('body')
    ]

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

    hero_image = models.ForeignKey(
        settings.IMAGE_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    base_blocks = [
        ImageChooserPanel('hero_image'),
        StreamFieldPanel('body'),
        StreamFieldPanel('additional_content'),
    ]

    content_panels = BasePage.content_panels + base_blocks

    search_fields = BasePage.search_fields + [
        index.SearchField('body'),
    ]

    @property
    def date(self):
        return self.display_date


####################################################################################################
# Content Page Type
####################################################################################################


class ArticlePageWithContentsType(ContentPageType):
    """
    An article page which as a long body requiring a contents listing
    """

    class Meta:
        abstract = True

    template = 'content/article_page_with_contents.jinja'

    body = fields.StreamField(contents_page_body_blocks, blank=True)

    def build_contents_menu(self):
        menu = []
        for block in self.body:
            if block.block_type == 'contents_menu_item':
                menu.append({
                    'slug': block.value.slug,
                    'title': block.value.get('title'),
                    'children': []
                })
            if block.block_type == 'contents_menu_sub_item':
                menu[-1]['children'].append({
                    'slug': block.value.slug,
                    'title': block.value.get('title')
                })
        return menu

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        context.update({
            'contents_menu': self.build_contents_menu()
        })

        return context
