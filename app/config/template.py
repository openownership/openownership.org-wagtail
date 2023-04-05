# stdlib
import os

# 3rd party
import arrow
import jinja2
from cacheops import cached
from consoler import console
from jinja2.ext import Extension
from django.conf import settings
from django.utils import translation
from django.shortcuts import reverse
from markupsafe import Markup
from django.utils.safestring import mark_safe
from django.template.defaultfilters import slugify
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import SafeString
from django.contrib.staticfiles.storage import staticfiles_storage
from wagtail.contrib.routable_page.templatetags.wagtailroutablepage_tags import routablepageurl

# Project
from modules.core.models import SiteImage


def picture(img: SiteImage, w: int, h: int, style: str = "fill", alt: str = '') -> str:
    """Try to output something like this...
        <picture>
            <source srcset="/media/cc0-images/surfer-240-200.jpg"
                    media="(min-width: 800px)">
            <img src="/media/cc0-images/painted-hand-298-332.jpg" alt="" />
        </picture>
    """
    if img is None:
        return ''
    sm = img.get_rendition(f"{style}-{int(w/2)}x{int(h/2)}")
    x1 = img.get_rendition(f"{style}-{w}x{h}")
    x2 = img.get_rendition(f"{style}-{w*2}x{h*2}")
    sm_url = sm.url
    x1_url = x1.url
    x2_url = x2.url
    if not len(alt):
        try:
            alt = img.alt_text
        except Exception as e:
            console.error(e)

        if alt is None:
            alt = ""
    rv = f"""
        <picture>
            <source srcset="{x1_url}, {x2_url} 2x" media="(min-width: 800px)">
            <img src="{sm_url}" srcset="{sm_url}, {x1_url} 2x" alt="{alt}">
        </picture>
    """
    return mark_safe(rv)


def contains_filter(haystack, needle):
    if needle in str(haystack):
        return True
    return False


def nl2br(value: str) -> Markup:
    """Escape, then convert newlines to br tags, then wrap with Markup object
    # so that the <br> tags don't get escaped.

    Returns:
        str: value but with new lines converted to br tags
    """
    def escape(s):
        return str(jinja2.escape(s))
    return Markup(escape(value).replace('\n', '<br>'))


def richtext_custom(value: str, wrapper=False) -> SafeString:
    from wagtail.rich_text import RichText, expand_db_html

    if isinstance(value, RichText):
        # passing a RichText value through the |richtext filter should have no effect
        return value
    elif value is None:
        html = ''
    else:
        html = expand_db_html(value)

    return mark_safe(html)


def checkbox(value):
    if value is True:
        return "YES"
    return "NO"


@cached(timeout=60 * 60 * 24 * 7)
def author_url(slug: str) -> str:
    """Takes an author slug and returns the author profile url

    Args:
        slug (str): Slug of the author's name, ie: bill-s-preston-esq

    Returns:
        str: The url for the author's profile
    """
    try:
        return reverse('profile', kwargs={'slug': slug})
    except Exception as e:
        console.warn(e)


def nicedate(value: str) -> str:
    if not value:
        return ""
    try:
        d = arrow.get(value)
    except Exception:
        return ""
    else:
        return d.format('DD MMMM YYYY')


def shortdate(value: str) -> str:
    try:
        d = arrow.get(value)
    except Exception:
        return None
    else:
        return d.format('DD/M/YY')


def nicedatetime(value: str) -> str:
    if value is None or value == '':
        return ''
    d = arrow.get(value)
    return d.format('DD MMM YYYY - h:mma')


def datestamp(value: str) -> str:
    try:
        d = arrow.get(value)
    except Exception:
        return None
    else:
        return d.format('DD MMM YYYY')


def fieldtype(field):
    return field.field.widget.__class__.__name__


def static(path):
    return '{}{}'.format(settings.STATIC_URL, path)


def yesno(value: str) -> str:
    if value is None:
        return ""

    # Handle fields sending other strings
    transformable = ["Yes", "No", True, False]
    if value not in transformable:
        console.info(f"Found non-y/n value {value}")
        return str(value)

    # console.info(value)
    if value:
        return _('Yes')
    else:
        return _('No')


def rich_text(value: str, class_name=None) -> SafeString:
    from django.utils.safestring import mark_safe
    from wagtail.rich_text import RichText, expand_db_html

    if isinstance(value, RichText):
        # passing a RichText value through the |richtext filter should have no effect
        source = expand_db_html(value.source)
        if class_name:
            return mark_safe(f'<div class="{class_name}">' + mark_safe(source) + '</div>')
        return mark_safe(source)
    elif value is None:
        html = ''
    else:
        if isinstance(value, str):
            html = expand_db_html(value)
        else:
            raise TypeError("""
                'richtext' template filter received an invalid value;
                expected string, got {}.""".format(type(value)))

    if class_name:
        return mark_safe(f'<div class="{class_name}">' + html + '</div>')
    return mark_safe(html)


def url_from_path(value):
    return value.replace('/home', '', 1)


def commitment_summary(commitment_type: str, country) -> SafeString:
    """Ported from the old map generator.

    Args:
        commitment_type (str): The commitment type
        country (CountryTag): A CountryTag

    Returns:
        SafeString: Description
    """
    root_domain = "https://www.openownership.org"
    gov = "https://www.gov.uk"
    if commitment_type == 'EU':
        return mark_safe(
            f"As a European Union member, {country.name} is obliged to "
            f"create a central, public register of beneficial ownership, "
            f"covering the whole economy."
        )
    elif commitment_type == 'EITI':
        return mark_safe(
            f"As an <a href='https://eiti.org/'>Extractives Industry "
            f"Transparency Initiative (EITI)</a> member, {country.name} has "
            f"committed to beneficial ownership transparency for the "
            f"extractives sector."
        )
    elif commitment_type == 'BOLG':
        return mark_safe(
            f"{country.name} has made a commitment to beneficial ownership "
            f"transparency as part of the "
            f"<a href='{root_domain}/what-we-do/the-beneficial-ownership-leadership-group/'>"
            f"Beneficial Ownership Leadership Group</a>."
        )
    elif commitment_type == 'UK Anti-Corruption Summit':
        return mark_safe(
            f"At the "
            f"<a href='{gov}/government/topical-events/anti-corruption-summit-london-2016'>"
            f"2016 UK Anti-Corruption Summit</a>, {country.name} made a "
            f"commitment to beneficial ownership disclosure."
        )
    elif commitment_type == 'OGP':
        return mark_safe(
            f"{country.name} has included a commitment in an Open "
            f"Government Partnership National Action Plan to beneficial "
            f"ownership transparency"
        )
    elif commitment_type == 'Other':
        return mark_safe(
            f"{country.name} has made a commitment to beneficial "
            f"ownership transparency through some other means"
        )
    return ""


def get_top_level_navpage(page, navbar_blocks):
    """
    Returns the top-most page above `page` in the navbar hierarchy.
    e.g. if, within some mega_nav and sub_menu structures we have:

    * About (mega_nav)
      * The Team (sub_menu)
        * Bob Ferris (link)

    and we call this with <Page: Bob Ferris> then this returns <Page: About>

    Returns None if `page` isn't found within the hierarchy.

    SPECIAL CASES:

    1. If page is a CountryView we use its breadcrumb_view property as
       the `page` instead (probably the Map page).

    2. If page is a Publication front or inner page, we use its
       parent/grandparent as the `page` instead (PublicationsIndexPage),
       because it will be in the navbar hierarchy, while the front/inner
       pages won't be.

    3. Similarly, TeamProfilePages or JobPages will use their parent
       pages to determine their place in the navbar hierarchy.

    * page is probably a Wagtail Page but it could also be a view
    * navbar_blocks is the navbar_blocks that was passed in the template context
    """
    from modules.content.models import (
        JobPage, PublicationFrontPage, PublicationInnerPage, TeamProfilePage
    )
    from modules.content.views import CountryView

    navpage = None

    if isinstance(page, CountryView):
        # Special case. If it's a CountryView, we want to show the same
        # nav as the Map page. Which is what a CountryView has as its
        # breadcrumb_page. So:
        page = page.breadcrumb_page
    elif isinstance(page, PublicationFrontPage):
        page = page.get_parent()
    elif isinstance(page, PublicationInnerPage):
        page = page.get_parent().get_parent()
    elif isinstance(page, TeamProfilePage) or isinstance(page, JobPage):
        page = page.get_parent()

    if hasattr(page, 'pk'):

        # Need to not only match this Page, but also its translated versions:
        page_pks = [page.pk] + [p.pk for p in page.get_translations()]

        for obj in navbar_blocks:
            navpage = obj['page']

            if hasattr(navpage, 'pk') and navpage.pk in page_pks:
                # If the current page is a top-level link in the navbar.
                return navpage

            if obj['type'] == 'mega_menu':
                for item in obj['objects']:
                    if item['page'] and item['page'].pk in page_pks:
                        return navpage

                    if item['type'] == 'sub_menu':
                        for sub_item in item['objects']:
                            if sub_item['page'] and sub_item['page'].pk in page_pks:
                                return navpage
        navpage = None
    return navpage


class TemplateGlobalsExtension(Extension):
    def __init__(self, environment):
        super(TemplateGlobalsExtension, self).__init__(environment)
        environment.filters.update({
            'nicedate': nicedate,
            'shortdate': shortdate,
            'yesno': yesno,
            'datestamp': datestamp,
            'fieldtype': fieldtype,
            'nl2br': nl2br,
            'contains': contains_filter,
            'rich_text': rich_text,
            'slugify': slugify,
            'url_from_path': url_from_path
        })
        environment.globals.update({
            'server_env': os.environ.get('SERVER_ENV'),
            'url': reverse,
            'checkbox': checkbox,
            'commitment_summary': commitment_summary,
            'static': staticfiles_storage.url,
            'picture': picture,
            'routablepageurl': jinja2.pass_context(routablepageurl),
            'get_top_level_navpage': get_top_level_navpage,
        })
        environment.install_gettext_translations(translation)
