"""
notion.reports

The Notion sync history, as a Wagtail admin report.

Answers one question: is the sync still working? Before this the only record of
a run was a Slack message, which Open Ownership cannot see and which scrolls
away, so a sync that stopped firing three weeks ago looked exactly like one that
succeeded an hour ago.

Follows `modules.feedback.views.reports` with three deliberate departures, each
noted where it happens.
"""

# 3rd party
import django_filters
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic.base import View
from wagtail.admin.auth import permission_denied
from wagtail.admin.filters import DateRangePickerWidget, WagtailFilterSet
from wagtail.admin.views.reports import ReportView
from wagtail.permission_policies import ModelPermissionPolicy

# Module
from modules.notion.models import SyncRun
from modules.notion.sync.runner import start_sync


class SyncRunFilterSet(WagtailFilterSet):
    class Meta:
        model = SyncRun
        fields = ["status", "dry_run", "started_at"]

    started_at = django_filters.DateFromToRangeFilter(
        label=_("Run at"),
        widget=DateRangePickerWidget,
    )
    status = django_filters.ChoiceFilter(
        label=_("Status"),
        choices=SyncRun.Status.choices,
        empty_label=_("All"),
    )
    dry_run = django_filters.BooleanFilter(label=_("Dry run"))


class SyncRunReportView(ReportView):
    """Every recorded sync run, newest first."""

    # Set as a class attribute rather than looked up in `__init__` the way the
    # feedback report does. There is no import cycle to dodge here, and the
    # listing machinery reads `model` for its own labels.
    model = SyncRun

    menu_title = _("Notion sync")
    # `page_title` is what the admin header renders. `ReportView.title` looks
    # like it should be, but nothing reads it, which is why the feedback report
    # next door has no heading either.
    page_title = _("Notion sync runs")
    page_subtitle = _("Whether the Notion data behind the site is up to date")
    title = page_title
    header_icon = "history"
    template_name = "reports/notion_sync.html"
    results_template_name = "reports/notion_sync_results.html"
    filterset_class = SyncRunFilterSet
    paginate_by = 50

    # Both URL names are registered, unlike the feedback report, so filtering
    # and paging swap the results rather than reloading the whole page.
    index_url_name = "notion_sync_report"
    index_results_url_name = "notion_sync_report_results"

    # A permission rather than a superuser check. Making this visible to Open
    # Ownership was the point of getting it off Slack, and they are editors.
    permission_policy = ModelPermissionPolicy(SyncRun)
    permission_required = "view"

    # `results` is deliberately absent: a JSON blob in a spreadsheet cell is
    # noise, and the counters beside it are what anyone would chart.
    export_headings = {
        "started_at": _("Started"),
        "finished_at": _("Finished"),
        "duration_display": _("Duration"),
        "status": _("Status"),
        "mode": _("Mode"),
        "scope": _("Databases"),
        "fetched": _("Fetched"),
        "created": _("Created"),
        "updated": _("Updated"),
        "skipped": _("Unchanged"),
        "deleted": _("Soft deleted"),
        "invalid_count": _("Invalid rows"),
        "missing_column_count": _("Missing columns"),
    }
    list_export = list(export_headings)

    def get_queryset(self):
        return SyncRun.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        last_full = SyncRun.objects.last_completed_full()
        context["last_full_run"] = last_full
        context["sync_is_stale"] = self._is_stale(last_full)
        context["stale_after_hours"] = int(
            settings.NOTION_SYNC_STALE_AFTER.total_seconds() // 3600,
        )
        context["sync_in_progress"] = self._sync_in_progress()
        return context

    def _sync_in_progress(self) -> bool:
        return SyncRun.objects.filter(status=SyncRun.Status.RUNNING).exists()

    def _is_stale(self, last_full) -> bool:
        """Whether to warn that the sync has stopped.

        Measured from the last full run that *completed*, whether or not it
        rejected rows: a run that could not read one row of 989 still proves the
        sync works. No completed full run at all counts as stale once anything
        has been recorded, which means every run since the history began either
        did not finish or was partial.
        """
        if not SyncRun.objects.exists():
            return False
        if not last_full:
            return True
        return timezone.now() - last_full.started_at > settings.NOTION_SYNC_STALE_AFTER


####################################################################################################
# Starting a sync from the page
####################################################################################################


class SyncTriggerView(View):
    """Start a sync from the report page.

    POST only. A GET that changed something would be triggered by a crawler, a
    link prefetch or a bookmark, and this one costs a few hundred calls to
    Notion's API.

    The work runs on a thread, so this returns immediately and the reader
    watches the run appear in the listing. Gated on the same permission as the
    report itself, so anyone who can see the status can also ask for a fresh one.
    """

    permission_policy = ModelPermissionPolicy(SyncRun)

    def post(self, request, *args, **kwargs):  # noqa: ARG002
        if not self.permission_policy.user_has_permission(request.user, "view"):
            return permission_denied(request)

        if SyncRun.objects.filter(status=SyncRun.Status.RUNNING).exists():
            # Two syncs writing the same tables at once is worth preventing, and
            # clicking twice is the obvious way to cause it.
            messages.warning(request, _("A sync is already running. Wait for it to finish."))
        else:
            start_sync()
            messages.success(request, _("Sync started. It will appear below as it progresses."))

        return redirect("notion_sync_report")
