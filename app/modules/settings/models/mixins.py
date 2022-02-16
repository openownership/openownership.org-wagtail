from cacheops import cached
from config.template import url_from_path
from django import forms
from django.conf import settings
from django.core.cache import cache
from django.db import models

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
        help_text='Analytics property ID (starting UA-...)',
        null=True,
        blank=True,
        max_length=32
    )

    tag_manager_property_id = models.CharField(
        help_text='Tag Manager property ID (starting GTM...)',
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
        ], heading="Analytics settings")
    ]


class MetaTagSettings(BaseSetting):

    class Meta:
        abstract = True

    meta_description = models.TextField(
        help_text='The short description shown in search results (160 characters max)',
        null=True,
        blank=True
    )

    meta_image = models.ForeignKey(
        settings.IMAGE_MODEL,
        help_text='A default image to use when shared on Facebook (aim for 1200x630)',
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
        ], heading="Meta Tag settings")
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


# class UpdateBannerSettings(BaseSetting):

#     class Meta:
#         abstract = True

#     body = models.CharField(
#         null=True,
#         blank=True,
#         max_length=255
#     )

#     link_page = models.ForeignKey(
#         'wagtailcore.Page',
#         null=True,
#         blank=True,
#         on_delete=models.SET_NULL
#     )

#     link_label = models.CharField(
#         null=True,
#         blank=True,
#         max_length=255,
#         default="Find out more"
#     )

#     live = models.BooleanField(
#         null=True,
#         blank=True
#     )

#     show_on_all_pages = models.BooleanField(
#         null=True,
#         blank=True
#     )

#     limit_to_pages = models.ManyToManyField(
#         'wagtailcore.Page',
#         blank=True,
#         related_name='update_banners'
#     )

#     @classmethod
#     @cached(timeout=settings.MONTH_IN_SECONDS)
#     def get_for_banner_context(cls, site, page):
#         obj = cls.for_site(site)
#         context = {}
#         if obj.live and any([
#             obj.show_on_all_pages, page.id in obj.limit_to_pages.values_list('id', flat=True)
#         ]):
#             context.update({
#                 'show_update_banner': True,
#                 'update_banner_body': obj.body,
#             })

#             if obj.link_page:
#                 context.update({
#                     'update_banner_link_href': url_from_path(getattr(obj.link_page, 'url_path')),
#                     'update_banner_link_label': obj.link_label
#                 })

#         return context

#     navigation_panels = [
#         MultiFieldPanel([
#             FieldPanel('body'),
#             MultiFieldPanel([
#                 PageChooserPanel('link_page'),
#                 FieldPanel('link_label'),
#             ], heading="CTA"),
#             FieldPanel('live', widget=forms.CheckboxInput),
#             FieldPanel('show_on_all_pages', widget=forms.CheckboxInput),
#             AutocompletePanel('limit_to_pages')
#         ], heading="Update banner settings")
#     ]


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
        menu.append({
            'type': 'mega_menu',
            'text': block.value['text'],
            'objects': []
        })
        current = next(
            i for i in menu if i['type'] == 'mega_menu' and i['text'] == block.value['text']
        )
        for obj in block.value['objects']:
            current['objects'].append({
                'section_title': obj.get('section_title'),
                'links': [(link.href, link.label) for link in obj.get('links')]
            })
        return menu

    @classmethod
    def get_nav_fields(cls):
        navbar_blocks = cls._meta.get_field('navbar_blocks').name
        return [navbar_blocks]

    navigation_panels = [
        MultiFieldPanel([
            StreamFieldPanel('navbar_blocks'),
        ], heading="Navbar"),
    ]


class Footer(BaseSetting):

    class Meta:
        abstract = True

    footer_nav = StreamField(
        footer_nav_blocks,
        blank=True,
        null=True
    )

    @classmethod
    def get_footer_nav_fields(cls):
        footer_nav = cls._meta.get_field('footer_nav').name
        return [footer_nav]

    navigation_panels = [
        MultiFieldPanel([
            StreamFieldPanel('footer_nav'),
        ], heading="Footer"),
    ]
