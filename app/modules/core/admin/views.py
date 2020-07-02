

# 3rd party
from django.urls import path
from django.shortcuts import reverse
from wagtail.admin.menu import MenuItem
from django.contrib.auth import get_user_model
from django.views.generic.list import ListView

# Module
from .forms import DocumentDownloadFilterForm


class DocumentDownloadsView(ListView):

    template_name = 'core/admin/downloads_list.html'
    paginate_by = 50
    context_object_name = 'downloads'
    page_kwarg = 'p'

    def get_form_data(self):

        return {
            'user': self.request.GET.get('user'),
            'document': self.request.GET.get('document')
        }

    def get_queryset(self):
        from modules.core.models import DocumentDownload
        form_data = self.get_form_data()
        query = DocumentDownload.objects

        if form_data.get('user', None):
            query = query.find(user_id=form_data.get('user'))

        if form_data.get('document', None):
            query = query.find(document_id=form_data.get('document'))

        return query.all()

    def users_queryset(self):
        return get_user_model().objects.filter(
            document_downloads__isnull=False
        ).distinct().order_by('username')

    def documents_queryset(self):
        from wagtail.documents.models import get_document_model
        _documents = get_document_model()
        return _documents.objects.filter(user_downloads__isnull=False).distinct().order_by('title')

    def get_context_data(self, *args, **kwargs):

        context = super().get_context_data(*args, **kwargs)

        filter_form = DocumentDownloadFilterForm(initial=self.get_form_data())

        filter_form.fields['user'].queryset = \
            self.users_queryset()
        filter_form.fields['document'].queryset = \
            self.documents_queryset()

        context.update({
            'filter_form': filter_form,
            'title': 'Document downloads'
        })

        return context


def admin_menus(request, menu_items):

    menus = [
        MenuItem(
            'Downloads',
            reverse('document_downloads'),
            classnames='icon icon-fa-download', order=850
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
