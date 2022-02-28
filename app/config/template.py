# stdlib
import os

# 3rd party
import arrow
from consoler import console
import jinja2
from jinja2.ext import Extension
from django.conf import settings
from django.shortcuts import reverse
from django.template.defaultfilters import slugify
from django.contrib.staticfiles.storage import staticfiles_storage
from django.utils import translation
from django.utils.safestring import mark_safe
from wagtail.contrib.routable_page.templatetags.wagtailroutablepage_tags import routablepageurl

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
    from django.utils.safestring import mark_safe
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
            'static': staticfiles_storage.url,
            'absolutepath': isabsolutepath,
            'picture': picture,
            'routablepageurl': jinja2.pass_context(routablepageurl),
            'now': time_now,
            'today': date_now
        })
        environment.tests.update({
            'absolutepath': isabsolutepath
        })
        environment.install_gettext_translations(translation)
