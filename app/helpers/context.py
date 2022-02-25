from consoler import console
from wagtail.core.models import Site
from wagtail.core.models import Locale
from modules.settings.models import NavigationSettings, SiteSettings


def _locales_context(context={}):
    """Context helper in case you need a list of all available locales in your page

    Args:
        context (dict, optional): Description

    Returns:
        TYPE: Description
    """
    locales = Locale.objects.all()
    response = []
    for locale in locales:
        try:
            response.append(
                {
                    'name': locale.get_display_name(),
                    'home': f"/{locale.language_code}/"
                }
            )
        except Exception as e:
            console.warn(e)
    context['locales'] = response
    return context


def global_context(context={}):
    """Update your context with things needed globally that are often only available on
    a Page model, but using this you can add them to views too.

    Returns:
        dict: Updated context
    """
    try:
        site = Site.objects.get(is_default_site=True)
        context = _locales_context(context)
        context.update(**SiteSettings.get_analytics_context(site)),
        context.update(**SiteSettings.get_social_context(site)),
        context.update(**NavigationSettings.get_nav_context(site)),
        # context.update(**GlobalContentSettings.get_global_settings_context(site)),
    except Exception as e:
        console.error(e)
        return {}
    else:
        context.update({
            'site_name': site.site_name
        })
        return context
