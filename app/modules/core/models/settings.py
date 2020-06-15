from cacheops import cached, invalidate_all

from django.db import models

from wagtail.contrib.settings.models import BaseSetting, register_setting
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.images import get_image_model_string
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtailcache.cache import clear_cache


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
        max_length=32)

    tag_manager_property_id = models.CharField(
        help_text='Tag Manager property ID (starting GTM...)',
        null=True,
        blank=True,
        max_length=32)

    @classmethod
    @cached(timeout=60 * 60 * 24)
    def get_for_context(cls, site):
        obj = cls.for_site(site)
        context = {}
        if obj.analytics_property_id:
            context['analytics_property_id'] = obj.analytics_property_id
        if obj.tag_manager_property_id:
            context['tag_manager_property_id'] = obj.tag_manager_property_id
        return context


@register_setting(icon="fa-share-alt")
class SocialMediaSettings(CachedSetting):

    class Meta:
        verbose_name = 'Social media accounts'

    facebook = models.URLField(
        help_text='Your Facebook page URL',
        null=True,
        blank=True)

    twitter = models.URLField(
        max_length=255, help_text='Full URL of Twitter profile',
        null=True,
        blank=True)

    @classmethod
    @cached(timeout=60 * 60 * 24)
    def get_for_context(cls, site):
        obj = cls.for_site(site)
        context = {'social_links': {}}
        field_names = [
            field.name for field in SocialMediaSettings._meta.fields
            if field.name not in ['id', 'site']
        ]

        for field in field_names:
            if getattr(obj, field):
                context['social_links'][field] = getattr(obj, field)

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
    @cached(timeout=60 * 60 * 24)
    def get_for_context(cls, site):
        obj = cls.for_site(site)
        return {
            'meta_description': obj.description,
            'meta_image': obj.image
        }
