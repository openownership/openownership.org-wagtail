import csv
from django.utils.translation import ugettext as _

from django.shortcuts import reverse
from django.conf.urls import url
from django.http import HttpResponse
from django.utils.encoding import smart_str
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.admin.filters import RelatedOnlyFieldListFilter
from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter

from wagtail.contrib.modeladmin.views import IndexView
from wagtail.contrib.modeladmin.helpers import ButtonHelper, AdminURLHelper, PermissionHelper


class ExportButtonHelper(ButtonHelper):
    """
    This helper constructs all the necessary attributes to create a button.
    There is a lot of boilerplate just for the classnames to be right :(
    """

    export_button_classnames = ['icon', 'icon-download']

    def export_button(self, classnames_add=None, classnames_exclude=None):
        if classnames_add is None:
            classnames_add = []
        if classnames_exclude is None:
            classnames_exclude = []

        classnames = self.export_button_classnames + classnames_add
        cn = self.finalise_classname(classnames, classnames_exclude)
        text = _('Export {}'.format(self.verbose_name_plural.title()))

        return {
            'url': self.url_helper.get_action_url('export', query_params=self.request.GET),
            'label': text,
            'classname': cn,
            'title': text,
        }


class ExportAdminURLHelper(AdminURLHelper):
    """
    This helper constructs the different urls.

    This is mostly just to overwrite the default behaviour
    which consider any action other than 'create', 'choose_parent' and 'index'
    as `object specific` and will try to add the object PK to the url
    which is not what we want for the `export` option.

    In addition, it appends the filters to the action.
    """

    non_object_specific_actions = ('create', 'choose_parent', 'index', 'export')

    def get_action_url(self, action, *args, **kwargs):
        query_params = kwargs.pop('query_params', None)

        url_name = self.get_action_url_name(action)
        if action in self.non_object_specific_actions:
            url = reverse(url_name)
        else:
            url = reverse(url_name, args=args, kwargs=kwargs)

        if query_params:
            url += '?{params}'.format(params=query_params.urlencode())

        return url

    def get_action_url_pattern(self, action):
        if action in self.non_object_specific_actions:
            return self._get_action_url_pattern(action)

        return self._get_object_specific_action_url_pattern(action)


class ExportView(IndexView):
    """
    Generic CSV export view
    """

    def __init__(self, *args, **kwargs):
        self.model_admin = kwargs.pop('model_admin')
        self.model = kwargs.pop('model')
        self.filename = kwargs.pop('filename')
        return super(ExportView, self).__init__(model_admin=self.model_admin, *args, **kwargs)

    def exclude_fields(self):
        return ['id', 'content_type', 'object_id']

    def export_csv(self):
        data = self.queryset.all()
        data_headings = [
            field.name.capitalize() for field in self.model._meta.get_fields()
            if field.name not in self.exclude_fields()
        ]
        fields = [
            field.name for field in self.model._meta.get_fields()
            if field.name not in self.exclude_fields()
        ]

        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment;filename={}'.format(self.filename)
        data_headings = [smart_str(label) for label in data_headings]

        writer = csv.writer(response)
        writer.writerow(data_headings)
        for row in data:
            data_row = []
            data_row.extend([getattr(row, field, None) for field in fields])
            writer.writerow(data_row)

        return response

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        super(ExportView, self).dispatch(request, *args, **kwargs)
        return self.export_csv()


class ExportModelAdminMixin(object):
    """
    Add this to your model admin to allow CSV downloads. You'll also need an ExportView for
    each model you want to be able to download.
    """

    button_helper_class = ExportButtonHelper
    url_helper_class = ExportAdminURLHelper

    def get_admin_urls_for_registration(self):
        urls = super(ExportModelAdminMixin, self).get_admin_urls_for_registration()
        urls += (
            url(
                self.url_helper.get_action_url_pattern('export'),
                self.export_view,
                name=self.url_helper.get_action_url_name('export')
            ),
        )

        return urls

    def export_view(self, request):
        kwargs = {'model_admin': self}
        view_class = self.export_view_class
        return view_class.as_view(**kwargs)(request)


class RelatedDropDownHelper(RelatedOnlyFieldListFilter, RelatedDropdownFilter):
    pass


class ReadOnlyPermissionHelper(PermissionHelper):
    def user_can_edit_obj(self, user, obj):
        return False  # Or any logic related to the user.

    def user_can_delete_obj(self, user, obj):
        return False  # Or any logic related to the user.

    def user_can_create(self, user):
        return False
