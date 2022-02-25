# 3rd party
from consoler import console
from django.http import Http404
from django.views.generic import TemplateView
from django.utils.datastructures import MultiValueDictKeyError

# Project
from helpers.context import global_context
from modules.notion.models import CountryTag


class CountryView(TemplateView):

    template_name = 'views/country.jinja'

    def __init__(self, *args, **kwargs):
        self.page_num = 1

    def setup(self, request, *args, **kwargs):
        try:
            self.page_num = int(request.GET['page'])
        except MultiValueDictKeyError:
            self.page_num = 1
        except Exception as e:
            console.error(e)
        super().setup(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = kwargs.pop('slug')
        tag = self._get_tag(slug)
        pages = self._get_pages(tag)
        context['tag'] = tag
        context['meta_title'] = f"{tag.name}"
        context['results'] = self._get_paginator(pages)
        global_context(context)  # Adds in nav settings etc.
        return context

    def _get_tag(self, slug):
        import ipdb; ipdb.set_trace()
        try:
            tag = CountryTag.objects.get(slug=slug)
        except CountryTag.DoesNotExist:
            raise Http404
        else:
            return tag
