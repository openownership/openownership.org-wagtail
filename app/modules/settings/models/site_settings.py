from cacheops import invalidate_all
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _

from .mixins import (
    AnalyticsSettings,
    MetaTagSettings,
    SocialMediaSettings,
    SearchSettings,
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
    SearchSettings,
    # UpdateBannerSettings
):

    class Meta:
        verbose_name = _('Site settings')

    def save(self, *args, **kwargs):
        cache.delete(self.get_cache_key_social(self.site_id))
        clear_cache()
        invalidate_all()
        return super().save(*args, **kwargs)

    base_tabs = [
        ObjectList(AnalyticsSettings.navigation_panels, heading=_('Analytics')),
        ObjectList(MetaTagSettings.navigation_panels, heading=_('Meta Tags')),
        ObjectList(SocialMediaSettings.navigation_panels, heading=_('Social media')),
        ObjectList(SearchSettings.search_panels, heading=_('Search')),
        # Not sure this is needed for OO:
        # ObjectList(UpdateBannerSettings.navigation_panels, heading=_('Update banner')),
    ]

    edit_handler = TabbedInterface(base_tabs)
