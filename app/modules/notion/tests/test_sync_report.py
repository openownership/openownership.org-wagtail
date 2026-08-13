"""Tests for the sync history report in the Wagtail admin.

The report answers "is the sync still working". These cover who can see it, the
banner that answers that question, and the failure detail that says what to fix.
"""

# stdlib
import datetime as dt

# 3rd party
import pytest
from django.contrib.auth.models import Group, Permission
from django.test import Client
from django.urls import reverse
from django.utils import timezone

# Module
from modules.notion.models import SyncRun
from modules.notion.report import SyncReport, SyncResult
from modules.notion.reports import SyncRunReportView

pytestmark = pytest.mark.django_db

URL = reverse("notion_sync_report")


####################################################################################################
# Helpers
####################################################################################################


@pytest.fixture
def superuser(django_user_model):
    return django_user_model.objects.create_superuser(
        email="boss@example.com",
        password="hunter2hunter2",  # noqa: S106
    )


@pytest.fixture
def editor(django_user_model):
    """An admin user with no permissions of their own, like Open Ownership."""
    user = django_user_model.objects.create_user(
        email="editor@example.com",
        password="hunter2hunter2",  # noqa: S106
    )
    user.is_staff = True
    user.save()
    user.user_permissions.add(Permission.objects.get(codename="access_admin"))
    return user


def allow(user):
    """Grant the permission the report is gated on."""
    user.user_permissions.add(Permission.objects.get(codename="view_syncrun"))
    return user


def signed_in(user) -> Client:
    client = Client()
    client.force_login(user)
    return client


def clean_report() -> SyncReport:
    report = SyncReport()
    report.add(SyncResult(name="countries", fetched=211, created=1))
    return report


def failing_report() -> SyncReport:
    report = SyncReport()
    result = SyncResult(name="impact", fetched=237)
    result.invalid.append(("3b2880fb-edf9-819e-8609-cba946cbd3e7", "description: too short"))
    report.add(result)
    return report


def aged(run: SyncRun, days: float) -> SyncRun:
    SyncRun.objects.filter(pk=run.pk).update(
        started_at=timezone.now() - dt.timedelta(days=days),
    )
    run.refresh_from_db()
    return run


####################################################################################################
# Who can see it
####################################################################################################


def test_an_admin_user_without_the_permission_is_refused(editor):
    assert signed_in(editor).get(URL).status_code in (302, 403)


def test_an_admin_user_with_the_permission_can_see_it(editor):
    assert signed_in(allow(editor)).get(URL).status_code == 200


def test_a_superuser_can_see_it(superuser):
    assert signed_in(superuser).get(URL).status_code == 200


def test_the_menu_item_is_hidden_without_the_permission(editor, rf):
    """Otherwise the sidebar offers a link straight to a refusal."""
    from modules.notion.wagtail_hooks import register_sync_report_menu_item

    request = rf.get("/admin/")
    request.user = editor

    assert register_sync_report_menu_item().is_shown(request) is False


def test_the_menu_item_is_shown_with_the_permission(editor, rf):
    from modules.notion.wagtail_hooks import register_sync_report_menu_item

    request = rf.get("/admin/")
    request.user = allow(editor)

    assert register_sync_report_menu_item().is_shown(request) is True


def test_the_permission_can_be_granted_through_the_admin():
    """Wagtail builds the group form's checkboxes only from the registered
    permissions hook, so without it nobody could grant this at all.
    """
    from modules.notion.wagtail_hooks import register_sync_run_permission

    assert register_sync_run_permission().filter(codename="view_syncrun").exists()


def test_the_editor_groups_are_granted_it_on_deploy():
    """The migration runs against the real groups, so Open Ownership see the
    report without anyone having to remember.
    """
    for name in ("Editors", "Moderators"):
        group = Group.objects.filter(name=name).first()
        if group:
            assert group.permissions.filter(codename="view_syncrun").exists()


####################################################################################################
# What it shows
####################################################################################################


def test_a_run_appears_in_the_listing(superuser):
    SyncRun.start().finish(clean_report())

    body = signed_in(superuser).get(URL).content.decode()

    assert "Succeeded" in body
    assert "211" in body


def test_a_failure_links_to_the_row_in_notion(superuser):
    """A reported problem has to be openable, not just readable."""
    SyncRun.start().finish(failing_report())

    body = signed_in(superuser).get(URL).content.decode()

    assert "https://www.notion.so/" in body
    assert "too short" in body


def test_a_crash_shows_why(superuser):
    SyncRun.start().finish(SyncReport(), error=ValueError("Notion timed out"))

    body = signed_in(superuser).get(URL).content.decode()

    assert "Notion timed out" in body


def test_a_dry_run_is_labelled_as_one(superuser):
    """So it is never mistaken for a real sync."""
    SyncRun.start(dry_run=True).finish(clean_report())

    body = signed_in(superuser).get(URL).content.decode()

    assert "Dry run" in body


def test_a_partial_run_names_the_databases_it_covered(superuser):
    SyncRun.start(only=["countries"]).finish(clean_report())

    body = signed_in(superuser).get(URL).content.decode()

    assert "countries" in body


####################################################################################################
# The staleness banner
####################################################################################################


def test_nothing_recorded_yet_says_so(superuser):
    body = signed_in(superuser).get(URL).content.decode()

    assert "No sync has been recorded yet" in body


def test_a_recent_success_reports_it(superuser):
    SyncRun.start().finish(clean_report())

    body = signed_in(superuser).get(URL).content.decode()

    assert "Last full sync completed" in body


def test_a_sync_that_rejected_a_row_still_reads_as_working(superuser):
    """The sync reached Notion and wrote what it could. A row Notion holds badly
    is data for Open Ownership to fix, and one bad row must not keep the warning
    on forever: nobody reads a banner that is always red.
    """
    SyncRun.start().finish(failing_report())

    body = signed_in(superuser).get(URL).content.decode()

    assert "Last full sync completed" in body
    assert "no successful full sync" not in body


def test_a_rejected_row_is_still_called_out_in_the_banner(superuser):
    SyncRun.start().finish(failing_report())

    body = signed_in(superuser).get(URL).content.decode()

    assert "needs fixing in Notion" in body


def test_a_sync_that_never_finished_warns(superuser):
    """This one really did not work."""
    SyncRun.start().finish(clean_report(), error=ValueError("Notion timed out"))

    body = signed_in(superuser).get(URL).content.decode()

    assert "no successful full sync" in body


def test_an_old_success_warns_that_the_sync_has_stopped(superuser):
    """The whole point of the report: a sync that stopped firing three weeks ago
    used to look exactly like one that ran an hour ago.
    """
    aged(SyncRun.start().finish(clean_report()), days=5)

    body = signed_in(superuser).get(URL).content.decode()

    assert "no successful full sync" in body


def test_a_dry_run_alone_does_not_count_as_a_successful_sync(superuser):
    SyncRun.start(dry_run=True).finish(clean_report())

    body = signed_in(superuser).get(URL).content.decode()

    assert "no successful full sync" in body


####################################################################################################
# Filtering and export
####################################################################################################


def test_the_status_filter_narrows_the_list(superuser):
    SyncRun.start().finish(clean_report())
    SyncRun.start().finish(failing_report())

    response = signed_in(superuser).get(f"{URL}?status=failures")

    assert [run.status for run in response.context["object_list"]] == ["failures"]


def test_the_run_history_exports_as_csv(superuser):
    SyncRun.start().finish(clean_report())

    response = signed_in(superuser).get(f"{URL}?export=csv")

    assert response.status_code == 200
    assert "text/csv" in response["Content-Type"]


def test_the_export_leaves_out_the_raw_json():
    """A blob of JSON in a spreadsheet cell helps nobody."""
    assert "results" not in SyncRunReportView.list_export


def test_the_page_has_a_heading(superuser):
    """`ReportView.title` looks like it would do this but nothing reads it, so
    the header stays blank unless `page_title` is set.
    """
    body = signed_in(superuser).get(URL).content.decode()

    assert "Notion sync runs" in body


def test_no_template_comment_leaks_onto_the_page(superuser):
    """Django only understands `{# #}` on a single line. A multi-line one is not
    a comment at all, it is text, and it renders straight onto the page.
    """
    SyncRun.start().finish(failing_report())

    body = signed_in(superuser).get(URL).content.decode()

    assert "{#" not in body
    assert "One row per sync run" not in body


####################################################################################################
# The failure detail
####################################################################################################


def test_the_failure_detail_reads_as_something_to_open(superuser):
    """The default disclosure marker is easy to miss against the admin's own
    styling, so the summary is given its own chevron and cursor.
    """
    SyncRun.start().finish(failing_report())

    body = signed_in(superuser).get(URL).content.decode()

    assert "sync-run-detail" in body


def test_the_per_database_counts_are_a_table(superuser):
    """A run of sentences cannot be compared down a column."""
    SyncRun.start().finish(failing_report())

    body = signed_in(superuser).get(URL).content.decode()

    assert "sync-run-detail__stats" in body
    assert "Unchanged" in body
    assert "Soft deleted" in body
