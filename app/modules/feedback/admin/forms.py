from django import forms
from ..models import FeedbackFormSubmission, FeedbackFormOption


def page_filter_choices():
    objs = FeedbackFormSubmission.objects.filter(description__isnull=False).values(
        'page_id', 'page__title').distinct().order_by("page__title")

    return [('', '--')] + [(obj['page_id'], obj['page__title']) for obj in objs]


def why_filter_choices():
    objs = FeedbackFormWhyOption.objects.values('id', 'label').order_by('sort_order')

    return [('', '--')] + [(obj['id'], obj['label']) for obj in objs]


def where_filter_choices():
    objs = FeedbackFormWhereOption.objects.values('id', 'label').order_by('sort_order')

    return [('', '--')] + [(obj['id'], obj['label']) for obj in objs]


class FilterForm(forms.Form):

    page_id = forms.ChoiceField(
        required=False,
        choices=page_filter_choices,
        label="Page"
    )

    why_id = forms.ChoiceField(
        required=False,
        choices=why_filter_choices,
        label="Why"
    )

    where_id = forms.ChoiceField(
        required=False,
        choices=where_filter_choices,
        label="Where"
    )
