# -*- coding: utf-8 -*-

"""
    content.models.mixins
    ~~~~~~~~~~~~~~~~~~
    Mixins and abstract page classes.
"""

from collections import OrderedDict

# 3rd party
from django.db import models
from django.conf import settings
from django_extensions.db.fields import AutoSlugField

from modelcluster.fields import ParentalManyToManyField
from modelcluster.models import ClusterableModel

from wagtail.core import fields
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel


class PageMixinBase(models.Model):
    """
    Add methods to this that you want all of your PageMixins to have.

    Mostly doing this to have a consistent way of handling panels across
    mixins and the pages that use them.
    """

    class Meta:
        abstract = True

    panels: list = []

    @classmethod
    def append_panels(cls, panels: list = []) -> list:
        """Takes a panels list from your page and appends the panels
        from this mixin.

        Args:
            panels (list): The page's panels list

        Returns:
            list: The page's panels with the mixin's panels appended.
        """
        return panels + cls.panels

    @classmethod
    def prepend_panels(cls, panels: list = []) -> list:
        """Takes a panels list from your page and prepends the panels
        from this mixin.

        Args:
            panels (list): The page's panels list

        Returns:
            list: The mixin's panels with the page's panels appended.
        """
        return cls.panels + panels


####################################################################################################
# Page Hero mixin
####################################################################################################

class PageHeroMixin(PageMixinBase):
    """
    This class can be used to add a generic hero to a page.
    """

    class Meta:
        abstract = True

    hero_headline = fields.RichTextField(
        blank=True,
        null=True,
        features=['bold'],
        verbose_name="Headline",
    )

    hero_body = fields.RichTextField(
        blank=True,
        null=True,
        features=['bold', 'italic', 'underline', 'link', 'document-link'],
        verbose_name="Body text"
    )

    hero_panels = [
        MultiFieldPanel([
            FieldPanel('hero_headline', classname="title"),
            FieldPanel('hero_body'),
        ], heading="Hero"),
    ]

    @property
    def has_hero(self):
        has_body = self.hero_body and self.hero_body != '<p></p>'
        if any([self.hero_headline, has_body]):
            return True
        return False

    def get_hero_context(self):

        context = {
            'has_hero': self.has_hero,
            'hero_headline': self.hero_headline,
            'hero_body': self.hero_body,
        }

        return context


####################################################################################################
# Taxonomy mixin
####################################################################################################


class TaxonomyHelperMixin(object):

    def get_m2m_tags(self):
        # Get list of titles and concatenate them
        tags = []

        for field in self.taxonomy_fields():
            if getattr(self, field.name) is not None:
                if isinstance(field, ParentalManyToManyField):
                    values = getattr(self, field.name).all().values_list('name', flat=True)
                    value = '\n'.join(x.strip() for x in values if x.strip() != '')
                    tags.append(value)
        return '\n'.join(tags)

    @classmethod
    def taxonomy_fields(cls):
        fields = []
        for _ in cls.taxonomy_panels:
            fields.append(getattr(cls, _.field_name).field)
        return fields

    @classmethod
    def taxonomy_options(cls):
        options = OrderedDict()
        for field in cls.taxonomy_fields():
            options.setdefault(field.name, {
                'name': field.verbose_name,
                'slug': field.name,
                'options': []
            })
            for option in field.related_model.objects.all():
                options[field.name]['options'].append(dict(slug=option.slug, name=option.name))
        return options


class TaxonomyObjectMixin(ClusterableModel):

    class Meta():
        ordering = ['name', ]
        abstract = True

    name = models.CharField('Name', max_length=255)
    slug = AutoSlugField('Slug', populate_from='name')
    autocomplete_search_field = 'name'

    panels = [
        FieldPanel('name'),
    ]

    def __str__(self):
        return self.name

    def autocomplete_label(self):
        return self.name
