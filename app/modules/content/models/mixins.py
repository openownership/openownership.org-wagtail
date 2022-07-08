# -*- coding: utf-8 -*-

"""
    content.models.mixins
    ~~~~~~~~~~~~~~~~~~
    Mixins and abstract page classes.
"""

# stdlib
from collections import OrderedDict

# 3rd party
from django.db import models
from django.conf import settings
from wagtail.core import fields
from wagtail.search import index
from modelcluster.fields import ParentalManyToManyField
from modelcluster.models import ClusterableModel
from django.utils.translation import gettext_lazy as _
from django_extensions.db.fields import AutoSlugField
from modelcluster.contrib.taggit import ClusterTaggableManager
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel

# Project
from modules.taxonomy.models import PublicationType
from modules.taxonomy.edit_handlers import PublicationTypeFieldPanel


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
        verbose_name=_("Headline"),
    )

    hero_body = fields.RichTextField(
        blank=True,
        null=True,
        features=settings.RICHTEXT_INLINE_FEATURES,
        verbose_name=_("Body text")
    )

    hero_panels = [
        MultiFieldPanel([
            FieldPanel('hero_headline', classname="title"),
            FieldPanel('hero_body'),
        ], heading=_("Hero")),
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

    def get_context(self, request, *args, **kwargs) -> dict:
        context = super().get_context(request, *args, **kwargs)
        if hasattr(self, 'hero_panels'):
            context.update(self.get_hero_context())
        return context

    @classmethod
    def get_admin_tabs(cls):
        """Add the hero tab to the tabbed interface
        """
        tabs = super().get_admin_tabs()
        tabs.insert(1, (cls.hero_panels, _("Hero")))
        return tabs


####################################################################################################
# Authors and Tags mixins
####################################################################################################


class AuthorsPageMixin(PageMixinBase):
    """
    For a page that can be assigned one or more Authors.
    """

    class Meta:
        abstract = True

    about_panels = [
        MultiFieldPanel(
            [InlinePanel('author_relationships', label=_('Authors'))], heading=_('Authors')
        )
    ]

    search_fields = [
        index.SearchField('_authors_string'),
    ]

    @classmethod
    def get_admin_tabs(cls):
        """Add the about tab to the tabbed interface
        """
        tabs = super().get_admin_tabs()
        tabs.insert(1, (cls.about_panels, _("About")))
        return tabs

    @property
    def authors(self):
        """Returns a list of Author objects associated with this article.
        """
        authors = self.author_relationships.all().order_by("sort_order")
        return [a.author for a in authors]

    @property
    def _authors_string(self):
        return ' '.join([a.name for a in self.authors])


class TaggedPageMixin(PageMixinBase):
    """
    For a page that has the several category / tags:

    * Publication type
    * Area of focus
    * Region
    * Sector
    """

    class Meta():
        abstract = True

    publication_type = models.ForeignKey(
        'taxonomy.PublicationType',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='pages_%(class)s',
    )

    areas_of_focus = ClusterTaggableManager(
        through='taxonomy.FocusAreaTaggedPage', blank=True
    )

    sectors = ClusterTaggableManager(
        through='taxonomy.SectorTaggedPage', blank=True
    )

    countries = ClusterTaggableManager(
        through='notion.CountryTaggedPage', blank=True
    )

    sections = ClusterTaggableManager(
        through='taxonomy.SectionTaggedPage', blank=True
    )

    principles = ClusterTaggableManager(
        through='taxonomy.PrincipleTaggedPage', blank=True
    )

    about_panels = [
        PublicationTypeFieldPanel('publication_type', _('Content type')),
        # FieldPanel('areas_of_focus', _('Areas of focus')),
        FieldPanel('sectors', _('Topics')),
        FieldPanel('countries', _('Countries')),
        FieldPanel('sections', _('Sections')),
        FieldPanel('principles', _('Open Ownership Principles')),
    ]

    search_fields = [
        index.SearchField('publication_type'),
        index.SearchField('areas_of_focus'),
        index.SearchField('sectors'),
        index.SearchField('countries'),
        index.SearchField('sections'),
        index.SearchField('principles'),
    ]

    @classmethod
    def get_admin_tabs(cls):
        """Add the about tab to the tabbed interface
        """
        tabs = super().get_admin_tabs()
        tabs.insert(1, (cls.about_panels, _("About")))
        return tabs

    @classmethod
    def get_publication_type_choices(cls):
        """
        Child classes can override this to restrict which PublicationTypes
        are available.
        """
        return PublicationType.objects.all()


class TaggedAuthorsPageMixin(TaggedPageMixin, AuthorsPageMixin):
    """
    For a page that has both Authors AND the categories/tags.

    Because I'm not sure how best to easily combine them into one admin panel.
    """

    class Meta():
        abstract = True

    about_panels = AuthorsPageMixin.about_panels + TaggedPageMixin.about_panels

    search_fields = [
        index.SearchField('_authors_string'),
    ]

    @classmethod
    def get_admin_tabs(cls):
        """Remove one of the TWO about tabs that the two combined mixins added.
        """
        tabs = super().get_admin_tabs()
        del tabs[1]
        return tabs


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
        for item in cls.taxonomy_panels:
            fields.append(getattr(cls, item.field_name).field)
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

    name = models.CharField(_('Name'), max_length=255)
    slug = AutoSlugField(_('Slug'), populate_from='name')
    autocomplete_search_field = 'name'

    panels = [
        FieldPanel('name'),
    ]

    def __str__(self):
        return self.name

    def autocomplete_label(self):
        return self.name
