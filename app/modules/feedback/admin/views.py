# 3rd party
from django.views import View
from django.shortcuts import reverse
from django.views.generic import ListView

# Project
from helpers.views import BaseTemplateView

# Module
from .forms import FilterForm
from ..models import (
    FeedbackFormMixin,
    FeedbackFormWhyOption,
    FeedbackFormWhereOption,
    FeedbackFormSubmission
)


_template_prefix = 'admin/feedback/'


class RatingsView(BaseTemplateView):
    template_name = '{}ratings_list.html'.format(_template_prefix)

    def get_context_data(self, **kwargs):
        context = super(RatingsView, self).get_context_data(**kwargs)

        feedback_counts = FeedbackFormMixin.get_feedback_counts()

        context['export_url'] = reverse('feedback_export')
        context['feedback_counts'] = feedback_counts

        context['feedback_options'] = FeedbackFormOption.objects.values(
            'id', 'label').order_by('sort_order')

        return context


class CommentsView(ListView):
    template_name = '{}comments_list.html'.format(_template_prefix)

    context_object_name = 'rows'

    def get_filter_form(self, data=None):
        return FilterForm(data)

    def get_form_data(self):
        filters = {}
        form = self.get_filter_form()
        for k, v in self.request.GET.items():
            if k in form.declared_fields.keys() and v:
                filters[k] = v

        return filters

    def get_queryset(self):

        query = FeedbackFormSubmission.objects\
            .filter(description__isnull=False)\

        filters = self.get_form_data()

        if filters:
            query = query.filter(**filters)

        return query.order_by('created_at')

    def get_context_data(self, *args, **kwargs):

        context = super(CommentsView, self).get_context_data(*args, **kwargs)

        context['export_url'] = reverse('feedback_export')
        context['filter_form'] = self.get_filter_form(self.get_form_data())

        return context


class ExportFeedbackCSV(View):
    csv_filename = 'feedback'
    prepend_fields = ['created_at']
    model = None

    def __init__(self, **kwargs):
        from ..models import FeedbackFormSubmission
        self.headers = self.get_headers()
        self.model = FeedbackFormSubmission

    def get_csv_filename(self):
        return '{}.csv'.format(self.csv_filename)

    def get_data(self):
        data = []
        for row in self.model.objects.all():
            data.append(self.process_row(row))
        return data

    def process_row(self, data):
        row = []
        row.extend(
            [
                data.page.title,
                data.page.url,
                data.option,
                data.description,
                data.created_at
            ]
        )
        return row

    def get_headers(self):
        return ['Page', 'URL', 'option', 'description', 'submitted']

    def render_to_csv(self):
        import csv
        from django.http import HttpResponse

        response = HttpResponse(content_type='text/csv')
        cd = 'attachment; filename="{0}"'.format(self.get_csv_filename())
        response['Content-Disposition'] = cd

        writer = csv.writer(response)
        writer.writerow(self.headers)

        for row in self.get_data():
            writer.writerow(row)

        return response

    def get(self, request, *args, **kwargs):
        return self.render_to_csv()
