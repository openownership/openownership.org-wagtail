from django.conf import settings
from django.db import models
from django.shortcuts import reverse
from django.utils.functional import cached_property

from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel

from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, PageChooserPanel, MultiFieldPanel
from wagtail.core.models import Orderable
from wagtail.documents.edit_handlers import DocumentChooserPanel

from wagtail.contrib.settings.models import BaseSetting, register_setting


class NestedInlinePanel(InlinePanel):
    def widget_overrides(self):
        widgets = {}
        child_edit_handler = self.get_child_edit_handler()
        for handler_class in child_edit_handler.children:
            widgets.update(handler_class.widget_overrides())
        widget_overrides = {self.relation_name: widgets}
        return widget_overrides


@register_setting(icon="fa-bars")
class PrimaryNavigationMenu(BaseSetting, ClusterableModel):
    """
    This class can be used to manage the primary navigation
    """

    class Meta():
        verbose_name = 'Primary navigation menu'

    highlighted_item_text = models.CharField(
        help_text='Link text',
        null=True,
        blank=True,
        max_length=32
    )

    highlighted_link_page = models.ForeignKey(
        'wagtailcore.Page',
        help_text='Link to a page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    panels = [
        NestedInlinePanel('nav_items', label="Items"),
        MultiFieldPanel([
            FieldPanel('highlighted_item_text'),
            PageChooserPanel('highlighted_link_page'),
        ], heading="Highlighted item")
    ]

    @cached_property
    def build(self):
        from copy import deepcopy
        queryset = self.nav_items.\
            order_by('sort_order')

        return deepcopy(queryset)

    @classmethod
    def get_for_context(cls, site):
        obj = cls.for_site(site)
        context = {
            'primary_nav': obj.build
        }

        if obj.highlighted_link_page:
            context.update({
                'primary_nav_highlight': {
                    'text': obj.highlighted_item_text or obj.highlighted_link_page.title,
                    'url': obj.highlighted_link_page.url_path.replace('/home', '', 1)
                }
            })

        return context


@register_setting(icon="fa-bars")
class FooterNavigationMenu(BaseSetting, ClusterableModel):
    """
    This class can be used to manage the primary navigation
    """

    class Meta():
        verbose_name = 'Footer navigation menu'

    panels = [
        NestedInlinePanel('nav_items', label="Items")
    ]

    @cached_property
    def build(self):
        from copy import deepcopy
        queryset = self.nav_items.\
            order_by('sort_order')

        return deepcopy(queryset)

    @classmethod
    def get_for_context(cls, site):
        obj = cls.for_site(site)
        return {'footer_nav': obj.build}


class NavItemBase(ClusterableModel, Orderable):

    class Meta():
        ordering = ['sort_order']
        abstract = True

    text = models.CharField(
        help_text='Link text',
        null=True,
        blank=True,
        max_length=32
    )

    link_page = models.ForeignKey(
        'wagtailcore.Page',
        help_text='Link to a page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    link_document = models.ForeignKey(
        settings.WAGTAILDOCS_DOCUMENT_MODEL,
        help_text='Link to a document',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    link_url = models.CharField(
        help_text='Link to an external URL',
        null=True,
        blank=True,
        max_length=255
    )

    panels = [
        FieldPanel('text'),
        PageChooserPanel('link_page'),
        DocumentChooserPanel('link_document'),
        FieldPanel('link_url'),
    ]

    @cached_property
    def url(self):
        if self.link_page:
            url = self.link_page.url_path.replace('/home', '', 1)
            return url
        if self.link_document:
            filename = self.link_document.file
            return reverse('wagtaildocs_serve', args=[self.link_document.id, filename])
        if self.link_url:
            return self.link_url

    def __str__(self):
        return self.text


class PrimaryNavHighlightItem(NavItemBase):
    pass


class PrimaryNavItem(NavItemBase):
    nav_menu = ParentalKey(
        'core.PrimaryNavigationMenu',
        related_name='nav_items',
        null=True,
        on_delete=models.CASCADE
    )

    panels = NavItemBase.panels + [
        NestedInlinePanel('children')
    ]


class PrimaryNavSubItem(NavItemBase):
    parent = ParentalKey(
        'core.PrimaryNavItem',
        related_name='children',
        null=True,
        on_delete=models.CASCADE
    )


class FooterNavItem(NavItemBase):
    nav_menu = ParentalKey(
        'core.FooterNavigationMenu',
        related_name='nav_items',
        null=True,
        on_delete=models.CASCADE
    )
