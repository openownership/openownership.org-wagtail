from cacheops import cached
# from config.template import url_from_path
# from django import forms
from django.conf import settings
from django.core.cache import cache
from django.db import models
from django.utils.translation import gettext_lazy as _

from modules.settings.blocks import (
    footer_nav_blocks,
    navbar_blocks,
    social_media_blocks
)

from wagtail.admin.edit_handlers import (
    FieldPanel, MultiFieldPanel, PageChooserPanel, StreamFieldPanel
)

from wagtail.contrib.settings.models import BaseSetting
from wagtail.core.fields import StreamField
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtailautocomplete.edit_handlers import AutocompletePanel


####################################################################################################
# Site settings mixins
####################################################################################################


class AnalyticsSettings(BaseSetting):

    class Meta:
        abstract = True

    analytics_property_id = models.CharField(
        help_text=_('Analytics property ID (starting UA-...)'),
        null=True,
        blank=True,
        max_length=32
    )

    tag_manager_property_id = models.CharField(
        help_text=_('Tag Manager property ID (starting GTM...)'),
        null=True,
        blank=True,
        max_length=32
    )

    @classmethod
    @cached(timeout=settings.MONTH_IN_SECONDS)
    def get_analytics_context(cls, site):
        obj = cls.for_site(site)
        context = {}
        if obj.analytics_property_id:
            context['analytics_property_id'] = obj.analytics_property_id
        if obj.tag_manager_property_id:
            context['tag_manager_property_id'] = obj.tag_manager_property_id
        return context

    navigation_panels = [
        MultiFieldPanel([
            FieldPanel('analytics_property_id'),
            FieldPanel('tag_manager_property_id'),
        ], heading=_("Analytics settings"))
    ]


class MetaTagSettings(BaseSetting):

    class Meta:
        abstract = True

    meta_description = models.TextField(
        help_text=_('The short description shown in search results (160 characters max)'),
        null=True,
        blank=True
    )

    meta_image = models.ForeignKey(
        settings.IMAGE_MODEL,
        help_text=_('A default image to use when shared on Facebook (aim for 1200x630)'),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    @classmethod
    @cached(timeout=settings.MONTH_IN_SECONDS)
    def get_metatag_context(cls, site):
        obj = cls.for_site(site)
        context = {}
        if obj.meta_description:
            context['meta_description'] = obj.meta_description
        if obj.meta_image:
            context['meta_image'] = obj.meta_image
        return context

    navigation_panels = [
        MultiFieldPanel([
            FieldPanel('meta_description'),
            ImageChooserPanel('meta_image')
        ], heading=_("Meta Tag settings"))
    ]


class SocialMediaSettings(BaseSetting):

    class Meta:
        abstract = True

    social_accounts = StreamField(
        social_media_blocks,
        blank=True,
        null=True
    )

    @classmethod
    def get_social_context(cls, site):
        obj = cls.for_site(site)
        cache_key = cls.get_cache_key_social(site.pk)
        cached = cache.get(cache_key)

        if not cached:
            obj = cls.for_site(site)
            data = obj.build_social()
            cache.set(cache_key, data, settings.MONTH_IN_SECONDS)  # month
            return data

        return cached

    @classmethod
    def get_cache_key_social(cls, site_id):
        return f'{site_id}_site_social_settings'

    def build_social(self):
        context = {'social_links': {}}
        for obj in self.social_accounts.raw_data:
            context['social_links'].update({
                obj['value']['service']: obj['value']['url']
            })
        return context

    navigation_panels = [
        StreamFieldPanel('social_accounts')
    ]


####################################################################################################
# Navigation settings mixins
####################################################################################################


class NavBar(BaseSetting):

    class Meta:
        abstract = True

    navbar_blocks = StreamField(
        navbar_blocks,
        blank=True,
        null=True
    )

    def build_mega_menu(self, block, menu):

        # In the dicts below, 'link' is useful for linking to whatever
        # Page, Doc or URL is in the menu.
        # But 'page' is useful for checking whether the Page being
        # viewed is the same as this menu item.

        nav_item = block.value['nav_item']
        menu.append({
            'type': 'mega_menu',
            'link': (nav_item.href, nav_item.label),
            'page': nav_item.get('link_page', None),
            'objects': []
        })
        current = next(
            i for i in menu if i['type'] == 'mega_menu' and i['link'][0] == nav_item.href
        )
        for sub_block in block.value['objects']:
            if sub_block.block_type == 'nav_item':
                sub_nav_item = sub_block.value
                current['objects'].append({
                    'type': 'nav_item',
                    'link': (sub_nav_item.href, sub_nav_item.label),
                    'page': sub_nav_item.get('link_page', None),
                })
            else:
                # sub_block.block_type == 'sub_menu'
                sub_nav_item = sub_block.value.get('nav_item')
                sub_nav_objects = []
                for link in sub_block.value.get('links'):
                    sub_nav_objects.append({
                        'link': (link.href, link.label),
                        'page': link.get('link_page', None),
                    })
                current['objects'].append({
                    'type': 'sub_menu',
                    'link': (sub_nav_item.href, sub_nav_item.label),
                    'page': sub_nav_item.get('link_page', None),
                    'objects': sub_nav_objects,
                })
        return menu

    @classmethod
    def get_nav_fields(cls):
        navbar_blocks = cls._meta.get_field('navbar_blocks').name
        return [navbar_blocks]

    navigation_panels = [
        MultiFieldPanel([
            StreamFieldPanel('navbar_blocks'),
        ], heading=_("Navbar")),
    ]


class Footer(BaseSetting):

    class Meta:
        abstract = True

    footer_nav = StreamField(
        footer_nav_blocks,
        blank=True,
        null=True
    )

    footer_nav2 = StreamField(
        footer_nav_blocks,
        blank=True,
        null=True
    )

    @classmethod
    def get_footer_nav_fields(cls):
        footer_nav = cls._meta.get_field('footer_nav').name
        footer_nav2 = cls._meta.get_field('footer_nav2').name
        return [footer_nav, footer_nav2]

    navigation_panels = [
        MultiFieldPanel([
            StreamFieldPanel('footer_nav', _('Legal')),
            StreamFieldPanel('footer_nav2', _('Contact')),
        ], heading=_("Footer")),
    ]
