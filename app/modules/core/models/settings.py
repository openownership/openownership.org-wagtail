from cacheops import cached, invalidate_all

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.db import models

from modelcluster.fields import ParentalManyToManyField

from wagtail.core.fields import StreamField
from wagtail.core.models import Page

from wagtail.contrib.settings.models import BaseSetting, register_setting
from wagtail.admin.edit_handlers import (
    FieldPanel, StreamFieldPanel, PageChooserPanel, MultiFieldPanel
)
from wagtail.images import get_image_model_string
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtailcache.cache import clear_cache

from wagtailautocomplete.edit_handlers import AutocompletePanel

from config.template import url_from_path

from modules.content.blocks.settings import (
    single_tiered_navigation_menu_blocks, two_tiered_navigation_menu_blocks,
    social_media_blocks
)


################################################################################
# Settings models
################################################################################

class CachedSetting(BaseSetting):

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        model = super().save(*args, **kwargs)
        clear_cache()
        invalidate_all()
        return model


@register_setting(icon="fa-bar-chart")
class AnalyticsSettings(CachedSetting):

    class Meta:
        verbose_name = 'Analytics settings'

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
    def get_for_context(cls, site):
        obj = cls.for_site(site)
        context = {}
        if obj.analytics_property_id:
            context['analytics_property_id'] = obj.analytics_property_id
        if obj.tag_manager_property_id:
            context['tag_manager_property_id'] = obj.tag_manager_property_id
        return context


@register_setting(icon="fa-info")
class MetaTagSettings(CachedSetting):

    class Meta:
        verbose_name = 'Meta and social sharing tags'

    description = models.TextField(
        help_text='The short description shown in search results (160 characters max)',
        null=True,
        blank=True
    )

    image = models.ForeignKey(
        get_image_model_string(),
        help_text='A default image to use when shared on Facebook (aim for 1200x630)',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    panels = [
        FieldPanel('description'),
        ImageChooserPanel('image')
    ]

    @classmethod
    @cached(timeout=settings.MONTH_IN_SECONDS)
    def get_for_context(cls, site):
        obj = cls.for_site(site)
        return {
            'meta_description': obj.description,
            'meta_image': obj.image
        }


@register_setting(icon="fa-share-alt")
class SocialMediaSettings(BaseSetting):

    class Meta:
        verbose_name = 'Social media accounts'

    accounts = StreamField(
        social_media_blocks,
        blank=False,
        null=True
    )

    panels = [
        StreamFieldPanel('accounts')
    ]

    def build(self):
        context = {'social_links': {}}
        for block in self.accounts.stream_data:
            value = block['value']
            context['social_links'].update({
                value['service']: value['url']
            })
        return context

    def save(self, *args, **kwargs):
        cache.delete(self.get_cache_key(self.site_id))
        return super().save(*args, **kwargs)

    @classmethod
    def get_cache_key(cls, site_id):
        return f'{site_id}_social_media_settings'

    @classmethod
    def get_for_context(cls, site):
        obj = cls.for_site(site)
        cache_key = cls.get_cache_key(site.pk)
        cached = cache.get(cache_key)

        if not cached:
            obj = cls.for_site(site)
            data = obj.build()
            cache.set(cache_key, data, settings.MONTH_IN_SECONDS)  # month
            return data

        return cached


@register_setting(icon="fa-bars")
class NavigationSettings(BaseSetting):

    primary_nav = StreamField(
        two_tiered_navigation_menu_blocks,
        blank=False,
        null=True
    )

    footer_nav = StreamField(
        single_tiered_navigation_menu_blocks,
        blank=False,
        null=True
    )

    panels = [
        StreamFieldPanel('primary_nav', classname="nav-settings"),
        StreamFieldPanel('footer_nav', classname="nav-settings")
    ]

    def build(self):
        menus = {}
        for nav_menu in self.get_nav_fields():
            menu = menus[nav_menu] = []
            for block in getattr(self, nav_menu):
                if block.block_type == 'sub_nav':
                    menu.append({
                        'type': 'sub_nav',
                        'text': block.value['text'],
                        'value': [
                            (obj.href, obj.label) for obj in block.value['objects']
                        ]
                    })
                else:
                    menu.append({
                        'type': 'nav_item',
                        'value': (block.value.href, block.value.label)
                    })
        return menus

    def save(self, *args, **kwargs):
        cache.delete(self.get_cache_key(self.site_id))
        return super().save(*args, **kwargs)

    @classmethod
    def get_cache_key(cls, site_id):
        return f'{site_id}_navigation_settings'

    @classmethod
    def get_nav_fields(cls):
        fields = []
        for field in cls._meta.fields:
            if type(field) == StreamField:
                fields.append(field.name)

        return fields

    @classmethod
    def get_for_context(cls, site):
        cache_key = cls.get_cache_key(site.pk)
        cached = cache.get(cache_key)
        if not cached:
            obj = cls.for_site(site)
            data = obj.build()
            cache.set(cache_key, data, settings.MONTH_IN_SECONDS)  # month
            return data
        return cached


@register_setting(icon="fa-exclamation-circle")
class UpdateBannerSettings(CachedSetting):

    class Meta:
        verbose_name = 'Update banner'

    body = models.CharField(
        null=True,
        blank=False,
        max_length=255
    )

    link_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    link_label = models.CharField(
        null=True,
        blank=False,
        max_length=255,
        default="Find out more"
    )

    live = models.BooleanField(
        null=True,
        blank=True
    )

    show_on_all_pages = models.BooleanField(
        null=True,
        blank=True
    )

    limit_to_pages = models.ManyToManyField(
        'wagtailcore.Page',
        blank=True,
        related_name='update_banners'
    )

    panels = [
        FieldPanel('body'),
        MultiFieldPanel([
            PageChooserPanel('link_page'),
            FieldPanel('link_label'),
        ], heading="CTA"),
        FieldPanel('live', widget=forms.CheckboxInput),
        FieldPanel('show_on_all_pages', widget=forms.CheckboxInput),
        AutocompletePanel('limit_to_pages')
    ]

    @classmethod
    @cached(timeout=settings.MONTH_IN_SECONDS)
    def get_for_context(cls, site, page):
        obj = cls.for_site(site)
        context = {}
        if obj.live and any([
            obj.show_on_all_pages, page.id in obj.limit_to_pages.values_list('id', flat=True)
        ]):
            context.update({
                'show_update_banner': True,
                'update_banner_body': obj.body,
            })

            if obj.link_page:
                context.update({
                    'update_banner_link_href': url_from_path(getattr(obj.link_page, 'url_path')),
                    'update_banner_link_label': obj.link_label
                })

        return context
