# 3rd party
import pytest
import arrow
from consoler import console  # NOQA
from django.apps import apps
from django.conf import settings
from wagtail.core.models import Page, Site, Collection, Locale
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType


pytestmark = pytest.mark.django_db


def fake_initial_migration():
    ContentType = apps.get_model('contenttypes.ContentType')
    Permission = apps.get_model('auth.Permission')
    Group = apps.get_model('auth.Group')
    wagtailadmin_content_type, created = ContentType.objects.get_or_create(
        app_label='wagtailadmin',
        model='admin'
    )

    # Create admin permission
    admin_permission, created = Permission.objects.get_or_create(
        content_type=wagtailadmin_content_type,
        codename='access_admin',
        name='Can access Wagtail admin'
    )

    # Assign it to Editors and Moderators groups
    for group in Group.objects.filter(name__in=['Editors', 'Moderators']):
        group.permissions.add(admin_permission)

    # And because Wagtail creates data in a migration file AGAIN
    for item in settings.WAGTAIL_CONTENT_LANGUAGES:
        code = item[0]
        loc = Locale()
        loc.language_code = code
        loc.save()


def fake_group_collection_migration():
    ctype = ContentType.objects.filter(model='groupcollectionpermission').first()
    Permission.objects.get_or_create(
        name="Can add group collection permission",
        content_type=ctype,
        codename='add_groupcollectionpermission'
    )
    Permission.objects.get_or_create(
        name="Can change group collection permission",
        content_type=ctype,
        codename='change_groupcollectionpermission'
    )
    Permission.objects.get_or_create(
        name="Can delete group collection permission",
        content_type=ctype,
        codename='delete_groupcollectionpermission'
    )
    Permission.objects.get_or_create(
        name="Can view group collection permission",
        content_type=ctype,
        codename='view_groupcollectionpermission'
    )


def add_root_collection():
    """ id:AutoField                   1
        path:CharField                 0001
        depth:PositiveIntegerField     1
        numchild:PositiveIntegerField  5
        name:CharField                 Root
    """
    Collection.objects.get_or_create(
        path="0001",
        depth=1,
        name="Root"
    )


def setup():
    """Use this one if you're doing a single language site.
    """
    console.warn('SETTING UP')
    fake_initial_migration()
    root = Page.objects.create(
        path='0001',
        depth=1,
        slug='root',
        title='root'
    )

    Site.objects.create(
        root_page_id=root.id,
        hostname='localhost',
        port=80,
        site_name="Test Site",
        is_default_site=True
    )

    fake_group_collection_migration()
    add_root_collection()


def setup_multilingual():
    """Use this one if you're doing a multi-language site.
    """
    console.warn('SETTING UP')
    from modules.content.models.pages import HomePage
    fake_initial_migration()
    root = Page.objects.create(
        path='0001',
        depth=1,
        slug='root',
        title='root'
    )

    p = HomePage()
    p.first_published_at = arrow.now().datetime
    p.title = 'Test Site Home EN'
    p.slug = 'en'
    root.add_child(instance=p)
    p.save_revision().publish()
    p.save()

    Site.objects.create(
        root_page_id=p.id,
        hostname='localhost',
        port=80,
        site_name="Test Site",
        is_default_site=True
    )
    fake_group_collection_migration()
    add_root_collection()
