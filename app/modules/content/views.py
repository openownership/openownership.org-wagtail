# 3rd party
from consoler import console
from django.utils.functional import cached_property
from django.http import Http404
from django.views.generic import TemplateView
from django.utils.datastructures import MultiValueDictKeyError
from wagtail.core.models import Locale

# Project
from helpers.context import global_context
from modules.notion.models import CountryTag
from modules.content.models import SectionPage, HomePage


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
        self.tag = self._get_tag(slug)
        context['tag'] = self.tag
        context['page'] = self
        context['meta_title'] = f"{self.tag.name}"
        global_context(context)  # Adds in nav settings etc.
        return context

    @cached_property
    def title(self):
        return self.tag.name

    @cached_property
    def section_page(self):
        """Country views appear as though inside the Impact section, so we look this up
        for the menu etc. first for the current locale, secondly for any locale, and
        if it fails to find one, it returns the HomePage just so that there's something.
        """
        try:
            page = SectionPage.objects.filter(locale=Locale.get_active(), slug='impact').get()
        except SectionPage.DoesNotExist:
            page = SectionPage.objects.filter(slug='impact').first()
            if not page:
                page = HomePage.objects.filter(locale=Locale.get_active()).first()

        return page

    def _get_tag(self, slug):
        try:
            tag = CountryTag.objects.get(slug=slug)
        except CountryTag.DoesNotExist:
            raise Http404
        else:
            return tag
