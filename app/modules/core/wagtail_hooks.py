# 3rd party
import wagtail.admin.rich_text.editors.draftail.features as draftail_features
from cacheops import invalidate_all
from django.conf import settings
from wagtail.core import hooks
from django.utils.html import format_html_join
from wagtailcache.cache import clear_cache
from wagtail.core.models import PageViewRestriction
from wagtail.admin.rich_text.converters.html_to_contentstate import InlineStyleElementHandler

# Project
from modules.core.models import DocumentDownload

# Module
from .admin.views import admin_urls, admin_menus


####################################################################################################
# Admin URLs
####################################################################################################


@hooks.register('insert_global_admin_js')
def admin_js():
    js_files = [
        'js/admin.min.js',
    ]
    js_includes = format_html_join(
        '\n', '<script src="{0}{1}"></script>',
        ((settings.STATIC_URL, filename) for filename in js_files)
    )
    return js_includes


@hooks.register('insert_global_admin_css')
def admin_css():
    css_files = ['css/admin.min.css']

    css_includes = format_html_join(
        '\n', '<link rel="stylesheet" href="{0}{1}?v=3">',
        ((settings.STATIC_URL, filename) for filename in css_files)
    )
    return css_includes


####################################################################################################
# Hooks
####################################################################################################


@hooks.register('before_serve_document')
def track_document_download(document, request):
    from urllib.parse import urlparse

    try:
        referrer = urlparse(request.META['HTTP_REFERER']).path
    except KeyError:
        referrer = None

    download = DocumentDownload(
        document=document,
        referrer_path=referrer
    )

    if request.user.is_authenticated:
        download.user = request.user

    download.save()


@hooks.register('before_serve_page', order=-1)
def check_group_restrictions(page, request, serve_args, serve_kwargs):

    """
    Need this here because Wagtail's default is to send users who don't meet group permissions
    to the login page, which isn't great because they're already logged in and it's an endless
    loop. So we check if they are logged in, then if in the group - if not send them to a
    generic error page, otherwise just return nothing and let Wagtail run the default.
    """
    from django.core import exceptions
    for restriction in page.get_view_restrictions():
        if not restriction.accept_request(request):
            if restriction.restriction_type == PageViewRestriction.GROUPS:
                if request.user.is_authenticated:
                    raise exceptions.PermissionDenied


hooks.register('construct_main_menu', admin_menus)
hooks.register('register_admin_urls', admin_urls)


####################################################################################################
# Draftail
####################################################################################################


@hooks.register('register_rich_text_features')
def register_strikethrough_feature(features):
    """
    Registering the `small` feature, which uses the `SMALL` Draft.js inline style type,
    and is stored as HTML with an `<small>` tag.
    """
    feature_name = 'small'
    type_ = 'SMALL'
    tag = 'small'

    # 2. Configure how Draftail handles the feature in its toolbar.
    control = {
        'type': type_,
        'label': 'SM',
        'description': 'Small',
        # This isn’t even required – Draftail has predefined styles for STRIKETHROUGH.
        # 'style': {'textDecoration': 'line-through'},
    }

    # 3. Call register_editor_plugin to register the configuration for Draftail.
    features.register_editor_plugin(
        'draftail',
        feature_name, draftail_features.InlineStyleFeature(control)
    )

    # 4.configure the content transform from the DB to the editor and back.
    db_conversion = {
        'from_database_format': {tag: InlineStyleElementHandler(type_)},
        'to_database_format': {'style_map': {type_: tag}},
    }

    # 5. Call register_converter_rule to register the content transformation conversion.
    features.register_converter_rule('contentstate', feature_name, db_conversion)

    features.default_features.append('small')


# 1. Use the register_rich_text_features hook.
@hooks.register('register_rich_text_features')
def register_underline_feature(features):
    """
    Registering the `underline` feature.
    """
    feature_name = 'underline'
    type_ = 'UNDERLINE'

    # 2. Configure how Draftail handles the feature in its toolbar.
    control = {
        'type': type_,
        'label': 'U',
        'description': 'underline',
    }

    # 3. Call register_editor_plugin to register the configuration for Draftail.
    features.register_editor_plugin(
        'draftail', feature_name,
        draftail_features.InlineStyleFeature(control)
    )

    # 4.configure the content transform from the DB and back.
    db_conversion = {
        'from_database_format': {
            'span[style="text-decoration: underline"]':
                InlineStyleElementHandler(type_)},
            'to_database_format': {
                'style_map': {
                    type_: 'span style="text-decoration: underline"'}},
    }

    # 5. Call register_converter_rule to register the conversion.
    features.register_converter_rule('contentstate', feature_name, db_conversion)
    features.default_features.append('underline')


@hooks.register('after_create_page')
@hooks.register('after_edit_page')
def clear_wagtailcache(request, page):
    if page.live:
        clear_cache()
        invalidate_all()
