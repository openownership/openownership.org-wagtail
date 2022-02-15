from .core import Category

from django.utils.translation import gettext_lazy as _


class PublicationType(Category):
    """
    e.g. Case Study, Guidance, Job.

    Some Pages should be set to have a specific type ("Job").
    Others can choose, but from a specific selection of types.
    """

    class Meta:
        verbose_name = _("Publication type")
        verbose_name_plural = _("Publication types")
