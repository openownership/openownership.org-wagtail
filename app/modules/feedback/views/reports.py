# 3rd party
import django_filters
from wagtail.core.models import Page
from django.apps import apps
from django.utils.translation import gettext_lazy as _
from wagtail.admin.auth import permission_denied
from wagtail.admin.views.reports import ReportView
from wagtail.admin.filters import (
    DateRangePickerWidget,
    WagtailFilterSet,
)
from ..models import FeedbackFormSubmission
from ..forms import WHY_CHOICES, WHERE_CHOICES


def get_feedback_page_queryset(request):
    return Page.objects.filter(
        pk__in=set(FeedbackFormSubmission.objects.values_list("page_id", flat=True))
    ).order_by('title')


class FeedbackFilterSet(WagtailFilterSet):

    class Meta:
        model = FeedbackFormSubmission
        fields = ["page", "why_option", "where_option", "created_at"]

    created_at = django_filters.DateFromToRangeFilter(
        label=_("Created at"), widget=DateRangePickerWidget
    )
    page = django_filters.ModelChoiceFilter(
        field_name="page", queryset=get_feedback_page_queryset
    )
    why_option = django_filters.ChoiceFilter(
        label=_("Why"),
        choices=WHY_CHOICES,
        empty_label=_("All"),
    )
    where_option = django_filters.ChoiceFilter(
        label=_("Where"),
        choices=WHERE_CHOICES,
        empty_label=_("All"),
    )



class FeedbackReportView(ReportView):

    menu_title = "Feedback"
    title = "Feedback form submissions"
    header_icon = "help"
    template_name = "reports/feedback.html"
    filterset_class = FeedbackFilterSet

    export_headings = {
        "page.title": _("Page"),
        "why_option": _("Why"),
        "where_option": _("Where"),
        "why_other": _("Why (other)"),
        "where_other": _("Where (other)"),
        "created_at": _("Submitted at"),
    }
    list_export = [
        "page.title",
        "why_option",
        "where_option",
        "why_other",
        "where_other",
        "created_at",
    ]

    def __init__(self, *args, **kwargs):
        self.model = apps.get_model('feedback.FeedbackFormSubmission')
        super().__init__(*args, **kwargs)

    def get_queryset(self):
        return self.model.objects.all()

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_superuser:
            return permission_denied(request)
        return super().dispatch(request, *args, **kwargs)
