# stdlib
import os

# 3rd party
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import ListView

from modules.core.paginator import DiggPaginator
from modules.core.utils import get_site_context


def error_context():
    from wagtail.core.models import Site

    context = {}
    site = Site.objects.get(is_default_site=True)
    context.update(**get_site_context())

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


class PaginatedListView(ListView):
    """
    Parent class for any other views that require pagination.
    """
    paginator_class = DiggPaginator

    # How many objects per page.
    # If left as None, then settings.PAGINATOR["objects_per_page"]
    # is used.
    paginate_by = None

    def get_paginate_by(self, queryset):
        if self.paginate_by:
            return self.paginate_by
        else:
            return settings.PAGINATOR["objects_per_page"]

    def get_paginator(
        self, queryset, per_page, orphans=0, allow_empty_first_page=True, **kwargs
    ):
        """The same as the default in ListView, but so we can pass in the
        custom arguments DiggPaginator uses.
        """
        sp = settings.PAGINATOR

        return self.paginator_class(
            queryset,
            per_page,
            orphans=orphans,
            allow_empty_first_page=allow_empty_first_page,
            body=sp['body'],
            margin=sp['margin'],
            padding=sp['padding'],
            tail=sp['tail'],
            **kwargs,
        )
