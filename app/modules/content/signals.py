import arrow
from wagtail.core.signals import page_published


def publish_page(sender, **kwargs):
    instance = kwargs['instance']
    if hasattr(instance, 'display_date') and instance.live:
        if not instance.display_date:
            instance.display_date = arrow.now().datetime
            instance.save()


page_published.connect(publish_page)
