# 3rd party
from consoler import console
from wagtail.core import hooks
from wagtail.contrib.modeladmin.options import ModelAdmin

# Module
from .models import Author


class AuthorModelAdmin(ModelAdmin):
    "Add 'Authors' item to admin sidebar"
    model = Author
    menu_icon = 'fa-user'
    list_display = ('name',)
    ordering = ('name',)


def publish_publication(request, page):
    """This is supposed to catch a publish action on either a PublicationFrontPage or a
    PublicationInnerPage, and then publish both the page and the chapter pages.
    """
    to_publish = []
    primary = False

    if page.__class__.__name__ == 'PublicationFrontPage':
        primary = page
    elif page.__class__.__name__ == 'PublicationInnerPage':
        primary = page.get_parent()

    if not primary:
        # we're publishing a different page type
        return

    to_publish.append(primary.get_latest_revision())
    for child in primary.get_children():
        to_publish.append(child.get_latest_revision())

    for item in to_publish:
        item.publish()
        item.page.live = True
        item.save()

    console.success("Published: ", to_publish)


def unpublish_publication(request, page):
    """This is supposed to catch an unpublish action on either a PublicationFrontPage or a
    PublicationInnerPage, and then unpublish both the page and the chapter pages.
    """
    to_unpublish = []
    primary = False

    if page.__class__.__name__ == 'PublicationFrontPage':
        primary = page
    elif page.__class__.__name__ == 'PublicationInnerPage':
        primary = page.get_parent()

    if not primary:
        # we're publishing a different page type
        return

    to_unpublish.append(primary)
    for child in primary.get_children():
        to_unpublish.append(child)

    for item in to_unpublish:
        item.unpublish()

    console.success("Unpublished: ", to_unpublish)


@hooks.register('after_publish_page')
def publish_entire_publication(request, page):
    publish_publication(request, page)


@hooks.register('after_unpublish_page')
def unpublish_entire_publication(request, page):
    unpublish_publication(request, page)
