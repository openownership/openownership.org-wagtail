# 3rd party
# stdlib
import csv

import arrow
from django.db import models
from django.http import HttpResponse
from django.urls import path
from django.contrib import messages
from django.shortcuts import reverse
from wagtail.documents import get_document_model
from wagtail.admin.menu import MenuItem
from django.views.generic.list import ListView

# Module
from .forms import DocumentDownloadFilterForm


class DocumentDownloadsView(ListView):

    template_name = 'core/admin/document_downloads_list.html'
    paginate_by = 50
    context_object_name = 'objs'
    page_kwarg = 'p'
    model = get_document_model()
    sort_fields = ['download_count', 'last_downloaded_at', 'title']
    default_sort_field = 'last_downloaded_at'
    default_sort_order = 'desc'
    filter_form = DocumentDownloadFilterForm

    def get_filters(self):

        query = self.request.GET
        filters = {}

        if query.get('title'):
            filters['title__icontains'] = query.get('title')

        if query.get('download_start_date'):
            filters['user_downloads__downloaded_at__gte'] = query.get('download_start_date')

        if query.get('download_end_date'):
            filters['user_downloads__downloaded_at__lte'] = query.get('download_end_date')

        if query.get('upload_start_date'):
            filters['created_at__gt'] = query.get('upload_start_date')

        if query.get('upload_end_date'):
            filters['created_at__lte'] = query.get('upload_end_date')

        if query.get('exclude_authenticated'):
            filters['user_downloads__user'] = None

        if query.get('exclude_empty'):
            filters['user_downloads__isnull'] = False

        return filters

    def get_sort_order(self):
        return self.request.GET.get('sort_order', self.default_sort_order)

    def get_sort_field(self):
        return self.request.GET.get('sort_field', self.default_sort_field)

    def get_ordering(self):
        sort_field = self.get_sort_field()
        sort_order = self.get_sort_order()

        if sort_field not in self.sort_fields:
            messages.warning(
                self.request,
                f'"{sort_field}" is not a valid sort field, using "{self.default_sort_field}"'
            )
            sort_field = self.default_sort_field

        if sort_order not in ['asc', 'desc']:
            messages.warning(
                self.request,
                f'"{sort_order}" is not a valid sort order, using "{self.default_sort_order}"'
            )
            sort_order = self.default_sort_order

        if sort_order == 'desc':
            return [models.F(sort_field).desc(nulls_last=True), ]
        else:
            return [models.F(sort_field).asc(nulls_last=True), ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        filter_form = DocumentDownloadFilterForm(self.request.GET)

        view_url = reverse(self.request.resolver_match.view_name)
        query_string = self.request.GET.urlencode()
        export_csv_url = f'{view_url}?{query_string}&format=csv'

        context.update({
            'sort_field': self.get_sort_field(),
            'sort_order': self.get_sort_order(),
            'filter_form': filter_form,
            'today': arrow.now().format('YYYY-MM-DD'),
            'export_csv_url': export_csv_url,
        })

        return context

    def get_queryset(self):

        Document = get_document_model()
        ordering = self.get_ordering()

        objs = (
            Document
            .objects
            .prefetch_related('user_downloads')
        )

        filters = self.get_filters()

        if filters:
            q_object = models.Q()
            for k, v in filters.items():
                q_object &= models.Q(**{k: v})
            objs = objs.filter(q_object)

        objs = objs.annotate(
            download_count=models.Count('user_downloads'),
            last_downloaded_at=models.Max('user_downloads__downloaded_at')
        )

        return objs.order_by(*ordering)

    def get(self, request, *args, **kwargs):
        if self.request.GET.get('format') == 'csv':
            return self.export_as_csv()
        return super().get(request, *args, **kwargs)

    def export_as_csv(self):
        queryset = self.get_queryset()
        now = arrow.now().format('YYYY-MM-DD HH_mm_ss')
        filename = f'document_downloads_{now}.csv'
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': f'attachment; filename="{filename}"'},
        )

        writer = csv.writer(response)
        writer.writerow(['Document', 'Downloads', 'Last downloaded', ])
        for row in queryset:
            writer.writerow([
                row.title,
                row.download_count,
                row.last_downloaded_at or 'Never'
            ])

        return response


def admin_menus(request, menu_items):

    menus = [
        MenuItem(
            'Downloads',
            reverse('document_downloads'),
            classnames='icon icon-download', order=850
        )
    ]
    for menu in menus:
        menu_items.append(menu)

    return menu_items


def admin_urls():
    from .views import DocumentDownloadsView
    return [
        path('document-downloads/', DocumentDownloadsView.as_view(), name='document_downloads'),
    ]
