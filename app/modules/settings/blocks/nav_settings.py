from django import forms
from wagtail.core import blocks
from wagtail.documents.blocks import DocumentChooserBlock
from modules.content.blocks.mixins import CTABlockStructValue


class NavItem(blocks.StructBlock):
    class Meta:
        form_template = 'wagtail/cta_block_form.html'
        label = 'Link'
        value_class = CTABlockStructValue
        icon = 'fa-link'
        form_classname = 'nav-settings'

    link_type = blocks.ChoiceBlock(
        choices=[
            ('page', 'Page'),
            ('document', 'Document'),
            ('url', 'URL'),
        ],
        widget=forms.RadioSelect,
        required=True,
        default='page',
    )

    link_page = blocks.PageChooserBlock(required=False, label="Linked Page")
    link_document = DocumentChooserBlock(required=False, label="Linked Document")
    link_url = blocks.CharBlock(required=False, label="URL")
    link_label = blocks.CharBlock(required=True)


class NavSubMenu(blocks.StructBlock):

    section_title = blocks.CharBlock(required=False)
    links = blocks.ListBlock(
        NavItem()
    )


class NavMegaMenu(blocks.StructBlock):

    class Meta:
        label = 'Link with mega menu'
        icon = 'fa-bars'

    text = blocks.CharBlock(required=False)
    objects = blocks.ListBlock(
        NavSubMenu()
    )