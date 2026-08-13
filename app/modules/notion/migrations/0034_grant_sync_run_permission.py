"""Let the existing editor groups see the Notion sync report.

The report exists so Open Ownership can tell whether the sync is working without
reading Slack, so it has to be visible on deploy rather than after someone
remembers to tick a box. Written to be a no-op if a group has been renamed or
removed, because a missing group is not a reason to fail a deploy.
"""

from django.db import migrations

GROUPS = ("Editors", "Moderators")
CODENAME = "view_syncrun"


def grant(apps, schema_editor):  # noqa: ARG001
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    permission = Permission.objects.filter(
        content_type__app_label="notion",
        codename=CODENAME,
    ).first()
    if not permission:
        return

    for name in GROUPS:
        group = Group.objects.filter(name=name).first()
        if group:
            group.permissions.add(permission)


def revoke(apps, schema_editor):  # noqa: ARG001
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    permission = Permission.objects.filter(
        content_type__app_label="notion",
        codename=CODENAME,
    ).first()
    if not permission:
        return

    for name in GROUPS:
        group = Group.objects.filter(name=name).first()
        if group:
            group.permissions.remove(permission)


class Migration(migrations.Migration):
    dependencies = [
        ("notion", "0033_syncrun"),
        # The permission rows this grants are created by the content types app
        # once the model's migration has run.
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.RunPython(grant, revoke),
    ]
