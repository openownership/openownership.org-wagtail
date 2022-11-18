# -*- coding: utf-8 -*-

"""
    blocks.mixins
    ~~~~~~~~~~~~~
    Add functionality to other blocks.
"""

# 3rd party
from django import forms
from wagtail.core import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.documents.blocks import DocumentChooserBlock


ALIGN_OPTIONS = [
    ('left', 'Left'),
    ('centred', 'Center'),
    ('right', 'Right'),
]


class EyebrowMixin(blocks.StructBlock):

    eyebrow = blocks.CharBlock(
        required=False,
        help_text="Small text that appears above the title"
    )


class TitleMixin(blocks.StructBlock):

    title = blocks.CharBlock(
        required=False
    )


class EyebrowTitleMixin(TitleMixin, EyebrowMixin):
    pass


class EyebrowTitleBodyMixin(TitleMixin, EyebrowMixin):
    body = blocks.RichTextBlock(
        required=False,
        features=['bold', 'italic', 'underline', 'ol', 'ul', 'small', 'link', 'document-link']
    )


class TitleBodyMixin(TitleMixin):

    body = blocks.RichTextBlock(
        required=False,
        features=['bold', 'italic', 'underline', 'ol', 'ul', 'small', 'link', 'document-link']
    )


class TitleSubBodyMixin(blocks.StructBlock):
    """Use when your block needs a title, subtitle and body text.

    Attributes:
        title (CharBlock): Description
        subtitle (CharBlock): Description
        body (CharBlock): Description
    """
    class Meta:
        abstract = True

    title = blocks.CharBlock(
        required=False,
        help_text="Title text."
    )
    subtitle = blocks.CharBlock(
        required=False,
        help_text="Title text."
    )
    body = blocks.RichTextBlock(
        required=False,
        help_text="Body text.",
        features=['bold', 'italic', 'underline', 'small', 'link', 'document-link']
    )


class ThemeMixin(blocks.StructBlock):

    """Choose a colour theme

    Attributes:
        colour (ChoiceBlock): Choose the colour theme for the block
    """

    class Meta:
        abstract = True

    COLOUR_OPTIONS: list = []

    colour = blocks.ChoiceBlock(
        choices=COLOUR_OPTIONS,
        required=True
    )


class ImageMixin(blocks.StructBlock):

    """Add an image with override for Alt text

    Attributes:
        image (ImageChooserBlock): The image to show
    """

    class Meta:
        abstract = True

    image = ImageChooserBlock(required=True)
    alttext = blocks.CharBlock(required=False, label="Alt text override")


####################################################################################################
# Link / CTA Mixins
####################################################################################################

class LinkLabelBlock(blocks.CharBlock):

    def __init__(self, required=True, help_text=None, max_length=None, min_length=None, **kwargs):
        super().__init__(**kwargs)
        self.field = forms.CharField(
            required=False,
            help_text="Text displayed on hyperlink, if required",
            max_length=max_length,
            min_length=min_length
        )


class LinkStructValue(blocks.StructValue):

    @property
    def link_label(self):
        if self.get('link_page'):
            return self.get('link_label') or self.get('link_page').title

        return self.get('link_label')

    @property
    def link_href(self):
        if self.get('link_page'):
            return getattr(self['link_page'], 'url', None)

        if self.get('link_document'):
            return getattr(self['link_document'], 'url', None)

        if self.get('link_url'):
            return self.get('link_url')


class CTABlockStructValue(blocks.StructValue):

    @property
    def link_type(self):
        return self.get('link_type')

    @property
    def label(self):
        if self.link_type != 'none':
            return self.get('link_label', 'Find out more')

    @property
    def href(self):

        if self.link_type == 'page':
            path = getattr(self.get('link_page'), 'url_path', None)
            if path:
                return path.replace('/home', '', 1)

        elif self.link_type == 'document':
            return getattr(self.get('link_document'), 'url')

        elif self.link_type == 'url':
            return self.get('link_url')

    @property
    def attrs(self):
        attrs = {}
        return attrs


class PageLinkMixin(blocks.StructBlock):

    link_page = blocks.PageChooserBlock(required=True, label="Linked Page")


class DocumentLinkMixin(blocks.StructBlock):

    link_document = DocumentChooserBlock(required=True, label="Linked Document")


class URLLinkMixin(blocks.StructBlock):
    # We use CharBlock, rather than URLBlock, so that something like /campaign-name/ would be valid
    link_url = blocks.CharBlock(required=True, label="URL")


####################################################################################################
# Link / CTA Partials
####################################################################################################

class ModelSelectBlock(blocks.ChooserBlock):
    target_model = None
    widget = forms.Select


class PageCTABlock(blocks.StructBlock):
    class Meta:
        verbose_name = "Page"
        icon = 'doc-empty-inverse'
        value_class = LinkStructValue

    link_page = blocks.PageChooserBlock(required=True, label="Linked Page")


class DocumentCTABlock(blocks.StructBlock):
    class Meta:
        icon = "doc-full"
        value_class = LinkStructValue

    link_document = DocumentChooserBlock(required=True, label="Linked Document")


class URLCTABlock(blocks.StructBlock):
    class Meta:
        icon = "fa-external-link-square"
        value_class = LinkStructValue

    link_url = blocks.CharBlock(required=True, label="URL")


class CTAStreamBlock(blocks.StreamBlock):
    class Meta:
        label = 'CTA'

    page = PageCTABlock(required=False)
    document = DocumentCTABlock(required=False)
    url = URLCTABlock(required=False)
