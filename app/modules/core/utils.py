from wagtail.core.models import Site


def get_site_context(site=None) -> dict:
    from modules.core.models import SocialMediaSettings, AnalyticsSettings, NavigationSettings

    if not site:
        try:
            site = Site.objects.get(is_default_site=True)
        except Site.DoesNotExist:
            raise Site.DoesNotExist('You need to set up a default Site in Wagtail')

    context = {}
    context.update(
        **NavigationSettings.get_for_context(site),
        **SocialMediaSettings.get_for_context(site),
        **AnalyticsSettings.get_for_context(site),

    )
    return context
