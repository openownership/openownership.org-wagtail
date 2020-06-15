
"""
    core.models.images
    ~~~~~~~~~~~~~~~~~~
    Custom image models.
"""

from django.db import models
from wagtail.images.models import Image as WagtailImage, AbstractImage, AbstractRendition


class SiteImage(AbstractImage):

    admin_form_fields = WagtailImage.admin_form_fields + (
        'alt_text',
    )

    alt_text = models.CharField(
        max_length=255,
        verbose_name="Alt text",
        blank=True,
        null=True
    )


class SiteImageRendition(AbstractRendition):
    class Meta:
        unique_together = (
            ('image', 'filter_spec', 'focal_point_key'),
        )

    image = models.ForeignKey(SiteImage, on_delete=models.CASCADE, related_name='renditions')


Rendition = SiteImageRendition
Image = SiteImage
