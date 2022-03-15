# stdlib
import os

# 3rd party
import json
import arrow
import jinja2
from cacheops import cached
from consoler import console
from jinja2.ext import Extension
from django.conf import settings
from django.utils import translation
from django.shortcuts import reverse
from django.utils.safestring import mark_safe
from django.template.defaultfilters import slugify
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
    sm_url = sm.url  # Faster if we only access this once
    x1_url = x1.url  # Faster if we only access this once
    x2_url = x2.url  # Faster if we only access this once
    if not len(alt):
        try:
            alt = img.alt
        except Exception as e:
            console.error(e)
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


def nl2br(self):
    # Escape, then convert newlines to br tags, then wrap with Markup object
    # so that the <br> tags don't get escaped.
    def escape(s):
        # unicode() forces the conversion to happen immediately,
        # instead of at substitution time (else <br> would get escaped too)
        return str(jinja2.escape(s))
    return jinja2.Markup(escape(self).replace('\n', '<br>'))


def richtext_custom(value, wrapper=False):
    from wagtail.core.rich_text import RichText, expand_db_html

    if isinstance(value, RichText):
        # passing a RichText value through the |richtext filter should have no effect
        return value
    elif value is None:
        html = ''
    else:
        html = expand_db_html(value)

    return mark_safe(html)


def isabsolutepath(value):
    if value.lower().startswith(("http://", 'https://')):
        return True
    else:
        return False


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


def nicedate(value):
    try:
        d = arrow.get(value)
    except Exception:
        return None
    else:
        return d.format('DD MMMM YYYY')


def shortdate(value):
    try:
        d = arrow.get(value)
    except Exception:
        return None
    else:
        return d.format('DD/M/YY')


def nicedatetime(value):
    if value is None or value == '':
        return ''
    d = arrow.get(value)
    return d.format('DD MMM YYYY - h:mma')


def datestamp(value):
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


def time_now():
    from datetime import datetime
    return datetime.utcnow()


def date_now():
    from datetime import date
    return date.today()


def rich_text(value, class_name=None):
    from django.utils.safestring import mark_safe
    from wagtail.core.rich_text import RichText, expand_db_html

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


def commitment_summary(commitment_type, country):
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
            f"<a href='https://www.openownership.org/what-we-do/the-beneficial-ownership-leadership-group/'>"
            f"Beneficial Ownership Leadership Group</a>."
        )
    elif commitment_type == 'UK Anti-Corruption Summit':
        return mark_safe(
            f"At the "
            f"<a href='https://www.gov.uk/government/topical-events/anti-corruption-summit-london-2016'>"
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


def get_subnav_top_level_page(page, navbar_blocks):
    """
    Returns the top-most page above `page` in the navbar hierarchy.
    e.g. if, within some mega_nav and sub_menu structures we have:

    * About (mega_nav)
      * The Team (sub_menu)
        * Bob Ferris (link)

    and we call this with page=<Bob Ferris> then this returns <About>

    Returns None if `page` isn't found within the hierarchy.
    """
    parent = None
    if hasattr(page, 'pk'):

        for obj in navbar_blocks:
            parent = obj['page']

            if obj['type'] == 'mega_menu':
                for item in obj['objects']:
                    if item['page'] and item['page'].pk == page.pk:
                        return parent

                    if item['type'] == 'sub_menu':
                        for sub_item in item['objects']:
                            if sub_item['page'] and sub_item['page'].pk == page.pk:
                                return parent

    return parent


class TemplateGlobalsExtension(Extension):
    def __init__(self, environment):
        super(TemplateGlobalsExtension, self).__init__(environment)
        environment.filters.update({
            'nicedate': nicedate,
            'shortdate': shortdate,
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
            'absolutepath': isabsolutepath,
            'picture': picture,
            'routablepageurl': jinja2.pass_context(routablepageurl),
            'now': time_now,
            'today': date_now,
            'get_subnav_top_level_page': get_subnav_top_level_page,
        })
        environment.tests.update({
            'absolutepath': isabsolutepath
        })
        environment.install_gettext_translations(translation)
