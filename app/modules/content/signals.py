import arrow
from django.db.models.signals import post_delete
from wagtail.search import index
from wagtail.signals import page_published, page_unpublished

from modules.content.models.pages import PublicationFrontPage, PublicationInnerPage


def publish_page(sender, **kwargs):  # noqa: ARG001
    instance = kwargs["instance"]
    if hasattr(instance, "display_date") and instance.live and not instance.display_date:
        instance.display_date = arrow.now().datetime
        instance.save()


page_published.connect(publish_page)


####################################################################################################
# Keep a publication's rolled-up search content fresh
####################################################################################################


def reindex_parent_publication(inner_page):
    """Reindex the parent PublicationFrontPage when one of its inner pages changes.

    The front page indexes its inner pages' content (see
    `PublicationFrontPage.get_inner_search_content`), and Wagtail only reindexes
    the saved object, so the parent would otherwise go stale until the next full
    `update_index`.
    """
    try:
        parent = inner_page.get_parent(update=True)
    except Exception:
        return

    if parent is None:
        return

    parent = parent.specific
    if not isinstance(parent, PublicationFrontPage):
        return

    # The parent may itself be mid-deletion (cascade); skip if it has gone.
    if not PublicationFrontPage.objects.filter(pk=parent.pk).exists():
        return

    index.insert_or_update_object(parent)


def reindex_parent_on_inner_change(sender, instance, **kwargs):  # noqa: ARG001
    reindex_parent_publication(instance)


page_published.connect(reindex_parent_on_inner_change, sender=PublicationInnerPage)
page_unpublished.connect(reindex_parent_on_inner_change, sender=PublicationInnerPage)
post_delete.connect(reindex_parent_on_inner_change, sender=PublicationInnerPage)
