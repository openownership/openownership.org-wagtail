from cacheops import invalidate_all
from django.core.cache import cache

from .mixins import (
    AnalyticsSettings,
    MetaTagSettings,
    SocialMediaSettings,
    # UpdateBannerSettings
)

from wagtail.admin.edit_handlers import ObjectList, TabbedInterface
from wagtail.contrib.settings.models import register_setting
from wagtailcache.cache import clear_cache


@register_setting(icon="fa-info")
class SiteSettings(
    AnalyticsSettings,
    MetaTagSettings,
    SocialMediaSettings,
    # UpdateBannerSettings
):

    class Meta:
        verbose_name = 'Site settings'

    def save(self, *args, **kwargs):
        cache.delete(self.get_cache_key_social(self.site_id))
        clear_cache()
        invalidate_all()
        return super().save(*args, **kwargs)

    base_tabs = [
        ObjectList(AnalyticsSettings.navigation_panels, heading='Analytics'),
        ObjectList(MetaTagSettings.navigation_panels, heading='Meta Tags'),
        ObjectList(SocialMediaSettings.navigation_panels, heading='Social media'),
        # Not sure this is needed for OO:
        # ObjectList(UpdateBannerSettings.navigation_panels, heading='Update banner'),
    ]

    edit_handler = TabbedInterface(base_tabs)
