# 3rd party
from django import forms
from cacheops import cached  # NOQA
from django.apps import apps
from wagtail import blocks
from wagtail.models import Page
from wagtail.images.blocks import ImageChooserBlock
from wagtail.documents.blocks import DocumentChooserBlock

# Module
from .mixins import (
    URLLinkMixin, PageLinkMixin, LinkStructValue, DocumentLinkMixin, CTABlockStructValue
)


####################################################################################################
# Link Cards
####################################################################################################

class PageCardBlock(PageLinkMixin):
    class Meta:
        verbose_name = "Page"
        icon = 'doc-empty-inverse'
        template = 'blocks/card.jinja'
        value_class = LinkStructValue

    def get_context(self, value, parent_context={}):
        context = super().get_context(value, parent_context=parent_context)
        page = getattr(value.get('link_page'), 'specific', None)
        if page:
            context.update({
                'title': page.title,
                'blurb': page.blurb,
                'thumbnail': page.thumbnail,
                'link_href': value.link_href,
                'link_label': value.link_label
            })

        return context


class DocumentCardBlock(DocumentLinkMixin):
    class Meta:
        icon = "doc-full"
        template = 'blocks/card.jinja'
        value_class = LinkStructValue

    title = blocks.CharBlock(
        required=False,
        help_text="Title text. If blank, we use the document title."
    )

    blurb = blocks.TextBlock(
        required=False,
        help_text="Blurb"
    )

    thumbnail = ImageChooserBlock(
        required=False,
    )

    def get_context(self, value, parent_context={}):
        context = super().get_context(value, parent_context=parent_context)
        document = value.get('link_document')
        if document:
            context.update({
                'title': value.get('title') or document.title,
                'blurb': value.get('blurb'),
                'thumbnail': value.get('thumbnail'),
                'link_href': value.link_href,
                'link_label': value.link_label
            })

        return context


class URLCardBlock(URLLinkMixin):
    class Meta:
        icon = "fa-external-link-square"
        template = 'blocks/card.jinja'
        value_class = LinkStructValue

    title = blocks.CharBlock(
        required=True,
    )

    blurb = blocks.TextBlock(
        required=True,
    )

    thumbnail = ImageChooserBlock(
        required=False,
    )

    def get_context(self, value, parent_context={}):
        context = super().get_context(value, parent_context=parent_context)
        document = value.get('link_url')
        if document:
            context.update({
                'title': value.get('title'),
                'blurb': value.get('blurb'),
                'thumbnail': value.get('thumbnail'),
                'link_href': value.link_href,
                'link_label': value.link_label
            })

        return context


class CardStreamBlock(blocks.StreamBlock):
    class Meta:
        icon = "fa-th-large"
        label = "Card group"

    page = PageCardBlock(required=False)
    document = DocumentCardBlock(required=False)
    url = URLCardBlock(required=False)


class LinkBlock(blocks.StructBlock):

    class Meta:
        form_template = 'wagtail/cta_block_form.html'
        label = "Link"
        value_class = CTABlockStructValue

    link_type = blocks.ChoiceBlock(
        choices=[
            ('none', 'None'),
            ('page', 'Page'),
            ('document', 'Document'),
            ('url', 'URL')
        ],
        widget=forms.RadioSelect,
        required=True,
        default='none',
    )

    link_page = blocks.PageChooserBlock(required=False, label="Linked Page")
    link_document = DocumentChooserBlock(required=False, label="Linked Document")
    link_url = blocks.CharBlock(required=False, label="URL")


class CTABlock(LinkBlock):

    class Meta:
        form_template = 'wagtail/cta_block_form.html'
        template = 'blocks/cta.jinja'
        label = "Link"
        value_class = CTABlockStructValue
        icon = "fa-link"

    link_label = blocks.CharBlock(
        required=False,
        help_text="If blank will display 'Find out more'"
    )


####################################################################################################
# Blocks
####################################################################################################

class PageListBlock(blocks.StructBlock):

    """Provides a list of pages of the specified Page type.
    Override the page by passing a str representation of a Page model
    path in your __init__. ie: self.model_str = 'eff.ArticlePage'
    """

    _model: Page = Page

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._limit = 10
        self._model_str = 'wagtailcore.Page'

    def _sort(self, query):
        """Override this to provide a different default sort order.

        Args:
            query (query): The query we're sorting on.
        """
        query.order_by('first_published_at').reverse()
        return query

    @cached(timeout=60 * 60)
    def get_cacheables(self) -> list:
        if not self._model:
            self._model = apps.get_model(self._model_str)
        query = self._model.objects
        objects = self._sort(query).all()[self._limit]

        return objects

    def get_context(self, value, parent_context={}):
        context = super().get_context(value, parent_context=parent_context)
        objects = self.get_cacheables()
        context['objects'] = objects

        return context


class ArticleImageBlock(blocks.StructBlock):

    class Meta:
        icon = "fa-file-image-o"
        template = "blocks/article_image.jinja"
        label = "Image"

    image = ImageChooserBlock(required=True)

    def get_context(self, value, parent_context={}):
        from wagtail.images.shortcuts import get_rendition_or_not_found
        context = super().get_context(value, parent_context=parent_context)
        if value.get('image'):
            context['image_'] = get_rendition_or_not_found(value['image'], 'original').img_tag()

        return context
