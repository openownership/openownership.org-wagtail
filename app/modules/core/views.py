# stdlib
import os

# 3rd party
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from wagtail.models import Page, Locale
from django.utils.translation import gettext_lazy as _

# Project
from modules.stats.models import ViewCount
from modules.content.forms import SearchForm
from modules.content.models import HomePage


def error_context():
    from wagtail.models import Site
    from modules.settings.models import NavigationSettings, SiteSettings

    context = {}
    site = Site.objects.get(is_default_site=True)
    context.update(
        **SiteSettings.get_analytics_context(site),
        **SiteSettings.get_metatag_context(site),
        **SiteSettings.get_social_context(site),
        **NavigationSettings.get_nav_context(site),
    )
    context.update({
        'site_name': settings.SITE_NAME,
        'error_page': True
    })
    return context


def error_400_view(request, exception):
    context = error_context()
    context['meta_title'] = '400: Server error'
    return render(request, 'errors/500.jinja', context=context, status=500)


def error_403_view(request, exception):
    context = error_context()
    context['meta_title'] = '403: permission denied'
    return render(request, 'errors/403.jinja', context=context, status=403)


def error_404_view(request, exception, status=404):
    context = error_context()
    page = HomePage.objects.first()
    page.headline = _('404: page not found')
    context['meta_title'] = page.headline
    context['page'] = page
    context['form'] = SearchForm(initial={
        'q': "",
        'pt': request.GET.getlist('pt', []),
        'pr': request.GET.getlist('pr', []),
        'sn': request.GET.getlist('sn', []),
        'sr': request.GET.getlist('sr', []),
    })

    popular_ids = ViewCount.objects.popular(7, 100)  # 3 popular articles from the last 7 days

    context['popular'] = Page.objects.filter(
        id__in=popular_ids,
        locale=Locale.get_active(),
    ).live().public()[:6]

    return render(request, 'errors/404.jinja', context=context, status=status)


def error_500_view(request):
    context = error_context()
    context['meta_title'] = '500: Server error'
    return render(request, 'errors/500.jinja', context=context, status=500)


def error_404_test(request):
    from django.http import Http404
    exc = Http404
    return error_404_view(request, exc, 500)


def robots(request):
    server_env = os.environ.get('SERVER_ENV')

    response = ''
    if server_env == 'production':
        response += 'User-agent: *\nDisallow: /admin/*\n'
    else:
        response += 'User-agent: *\nDisallow: /\n'

    response += "Sitemap: {}://{}/sitemap.xml".format(request.scheme, request.get_host())
    return HttpResponse(response, content_type="text/plain")
