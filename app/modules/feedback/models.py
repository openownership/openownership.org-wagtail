# 3rd party
from consoler import console
from uuid import uuid4
from django.db import models
from django.http import HttpResponseRedirect
from django_extensions.db.fields import (
    AutoSlugField, CreationDateTimeField, ModificationDateTimeField
)

# Project
from modules.content.models.mixins import PageMixinBase
from modules.feedback.forms import FeedbackForm


class FeedbackFormSubmission(models.Model):
    """A Django model for storing data submitted through FeedbackForm
    """

    class Meta:
        verbose_name_plural = 'Feedback'
        ordering = ['-created_at']

    id = models.UUIDField(primary_key=True, editable=False)

    page = models.ForeignKey(
        'wagtailcore.Page',
        blank=False,
        null=True,
        on_delete=models.SET_NULL,
        related_name="feedback"
    )

    why_option = models.CharField(
        blank=False,
        null=True,
        max_length=150,
        verbose_name="Why"
    )

    where_option = models.CharField(
        blank=False,
        null=True,
        max_length=150,
        verbose_name="Where"
    )

    why_other = models.TextField(
        blank=False,
        null=True,
        verbose_name="Other reason"
    )

    where_other = models.TextField(
        blank=False,
        null=True,
        verbose_name="Other reason"
    )

    created_at = CreationDateTimeField()
    updated_at = ModificationDateTimeField()

    def __str__(self):
        try:
            label = self.option.label
        except AttributeError:
            label = '?'
        return '<FeedbackFormSubmission {}: {}, {}>'.format(
            self.id, label, self.page_id
        )


class FeedbackMixin(PageMixinBase):

    class Meta:
        abstract = True

    def get_context(self, request, *args, **kwargs) -> dict:
        ctx = super().get_context(request, *args, **kwargs)
        ctx = self._inject_form(ctx)
        return ctx

    def serve(self, request, *args, **kwargs):
        self.request = request
        if request.method == 'POST':
            console.info(request.POST)
            form = FeedbackForm(request.POST)
            console.info("FeedbackMixin - Form submat!")
            if form.is_valid():
                console.info("FeedbackMixin - Form valid!")
                return self.form_valid(form)
            else:
                console.warn("FeedbackMixin - Form invalid!")
                return self.form_invalid(form)

        return super().serve(request, *args, **kwargs)

    def form_valid(self, form):
        """
        cleaned data comes through looking like this...
        {
            'x_phone': '',
            'why_downloading': 'other',
            'where_work': 'other',
            'why_other': 'free text entered by the user',
            'where_other': 'also free text entered by the user',
            'page_id': 43,
            'submission_id': UUID ('8dcd3b19-32e1-4260-9d50-e4ab37ed352a')
        }

        """
        try:
            data = form.cleaned_data
            if data['x_phone']:
                # Bot filled in the honeypot
                return HttpResponseRedirect(self.request.META.get('HTTP_REFERER'))

            console.info(data)
            sub = FeedbackFormSubmission()
            sub.page_id = int(data['page_id'])
            sub.id = uuid4()
            sub.why_option = data['why_downloading']
            sub.where_option = data['where_work']
            sub.why_other = data['why_other']
            sub.where_other = data['where_other']
            sub.save()
        except Exception as e:
            console.warn(e)

        return HttpResponseRedirect(self.request.META.get('HTTP_REFERER'))

    def form_invalid(self, form):
        data = form.cleaned_data
        console.error(data)
        import ipdb; ipdb.set_trace()
        return HttpResponseRedirect(self.request.META.get('HTTP_REFERER'))

    def _inject_form(self, ctx):
        from .forms import FeedbackForm
        ctx['feedback_form'] = FeedbackForm(
            initial={
                'page_id': self.id,
                'submission_id': uuid4(),
            }
        )
        return ctx

    # @classmethod
    # def get_feedback_counts(cls):

    #     option_ids = FeedbackFormOption.objects.values_list('pk', flat=True)
    #     count_queries = {}

    #     for option_id in option_ids:
    #         key = 'option_{}_count'.format(option_id)
    #         count_queries[key] = \
    #             Count(Case(When(
    #                 feedback__option_id=option_id, then=1), output_field=models.IntegerField()
    #             )
    #         )

    #     return Page.objects.filter(
    #         feedback__isnull=False).distinct().annotate(
    #         **count_queries).values(
    #         'id', 'title', *count_queries.keys()
    #     )
