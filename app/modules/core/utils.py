from django.conf import settings
from wagtail.models import Site


def get_site_context(site=None) -> dict:
    from modules.settings.models import NavigationSettings, SiteSettings

    if not site:
        try:
            site = Site.objects.get(is_default_site=True)
        except Site.DoesNotExist:
            raise Site.DoesNotExist('You need to set up a default Site in Wagtail')

    context = {
        "site_name": settings.SITE_NAME,
    }

    context.update(
        **SiteSettings.get_analytics_context(site),
        **SiteSettings.get_metatag_context(site),
        **SiteSettings.get_social_context(site),
        **NavigationSettings.get_nav_context(site),
    )

    return context
