# stdlib
import os

# 3rd party
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render


def error_context():
    from wagtail.core.models import Site
    from modules.core.models.settings import (
        SocialMediaSettings, AnalyticsSettings
    )

    context = {}
    site = Site.objects.get(is_default_site=True)
    context.update(**SocialMediaSettings.get_for_context(site))
    context.update(**AnalyticsSettings.get_for_context(site))
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


def error_404_view(request, exception):
    context = error_context()
    context['meta_title'] = '404: page not found'
    return render(request, 'errors/404.jinja', context=context, status=404)


def error_500_view(request):
    context = error_context()
    context['meta_title'] = '500: Server error'
    return render(request, 'errors/500.jinja', context=context, status=500)


def error_404_test(request):
    context = error_context()
    return render(request, 'errors/404.jinja', context=context, status=500)


def robots(request):
    server_env = os.environ.get('SERVER_ENV')

    response = ''
    if server_env == 'production':
        response += 'User-agent: *\nDisallow: /admin/*\n'
    else:
        response += 'User-agent: *\nDisallow: /\n'

    response += "Sitemap: {}://{}/sitemap.xml".format(request.scheme, request.get_host())
    return HttpResponse(response, content_type="text/plain")
