
"""
    core.models.documents
    ~~~~~~~~~~~~~~~~~~~~~
    Custom document models.
"""

# 3rd party
from django.db import models
from django.conf import settings
from wagtail.documents.models import Document as WagtailDocument
from wagtail.documents.models import AbstractDocument


class SiteDocument(AbstractDocument):

    admin_form_fields = WagtailDocument.admin_form_fields


Document = SiteDocument


################################################################################
# Statistic / Modeladmin models
################################################################################


class DocumentDownload(models.Model):

    document = models.ForeignKey(
        SiteDocument,
        null=True,
        on_delete=models.SET_NULL,
        related_name='user_downloads'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='document_downloads'
    )
    referrer_path = models.TextField(
        null=True,
        blank=True
    )
    downloaded_at = models.DateTimeField(auto_now_add=True, blank=True)
