from django.conf import settings
from consoler import console
from cacheops import cached
from wagtail.core.models import Site
from wagtail.core.models import Locale
from modules.settings.models import NavigationSettings, SiteSettings


def _locales_context(context: dict = {}) -> dict:
    """Context helper in case you need a list of all available locales in your page

    Args:
        context (dict, optional): Description

    Returns:
        dict: The context with locales added
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


def global_context(context: dict = {}) -> dict:
    """Update your context with things needed globally that are often only available on
    a Page model, but using this you can add them to views too.

    Returns:
        dict: Updated context
    """
    try:
        site = Site.objects.get(is_default_site=True)
        ctx = _locales_context(context)
        ctx.update(**SiteSettings.get_analytics_context(site)),
        ctx.update(**SiteSettings.get_social_context(site)),
        ctx.update(**NavigationSettings.get_nav_context(site)),
        ctx['press_links_page_url'] = _get_press_links_page_url()
        ctx['fflags'] = settings.FFLAGS
        console.info("1", ctx)
    except Exception as e:
        console.error(e)
        console.info("2", ctx)
        return {}
    else:
        context.update({
            'site_name': site.site_name
        })
        console.info("3", ctx)
        return context


@cached(timeout=60 * 60)
def _get_press_links_page_url():
    from modules.content.models.pages import PressLinksPage
    page = PressLinksPage.objects.filter(locale=Locale.get_active()).first()
    if page:
        return page.url
    else:
        return ''
