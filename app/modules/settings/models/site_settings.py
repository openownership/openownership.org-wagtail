# 3rd party
from cacheops import invalidate_all
from django.core.cache import cache
from wagtailcache.cache import clear_cache
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import ObjectList, TabbedInterface
from wagtail.contrib.settings.models import register_setting

# Module
from .mixins import SearchSettings, MetaTagSettings, AnalyticsSettings, SocialMediaSettings


@register_setting(icon="cogs")
class SiteSettings(
    AnalyticsSettings,
    MetaTagSettings,
    SocialMediaSettings,
    SearchSettings,
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
    ]

    edit_handler = TabbedInterface(base_tabs)
