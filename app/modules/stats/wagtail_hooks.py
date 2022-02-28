from consoler import console  # NOQA
from wagtail.core import hooks
from modules.stats.models import ViewCount


@hooks.register('before_serve_page')
def view_count_hit(page, request, serve_args, serve_kwargs):
    console.info('view_count_hit')
    if hasattr(page, 'is_countable') and page.is_countable is True:
        ViewCount.objects.hit(page.id)
