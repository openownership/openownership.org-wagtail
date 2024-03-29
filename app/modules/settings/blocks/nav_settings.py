# 3rd party
from django import forms
from wagtail import blocks
from wagtail.documents.blocks import DocumentChooserBlock

# Project
from modules.content.blocks.mixins import CTABlockStructValue


class NavItem(blocks.StructBlock):
    class Meta:
        form_template = 'wagtail/cta_block_form.html'
        label = 'Link'
        value_class = CTABlockStructValue
        icon = 'link'
        form_classname = 'nav-settings'

    link_type = blocks.ChoiceBlock(
        choices=[
            ('page', 'Page'),
            ('document', 'Document'),
            ('url', 'URL'),
        ],
        widget=forms.RadioSelect(),
        required=True,
        default='page',
    )

    link_page = blocks.PageChooserBlock(required=False, label="Linked Page")
    link_document = DocumentChooserBlock(required=False, label="Linked Document")
    link_url = blocks.CharBlock(required=False, label="URL")
    link_label = blocks.CharBlock(required=True)


class NavSubMenu(blocks.StructBlock):

    class Meta:
        label = 'Link with sub menu'
        icon = 'bars'

    nav_item = NavItem()
    links = blocks.ListBlock(
        NavItem()
    )


class NavMegaMenu(blocks.StructBlock):

    class Meta:
        label = 'Link with mega menu'
        icon = 'bars'

    nav_item = NavItem()
    objects = blocks.StreamBlock([
        ('nav_item', NavItem()),
        ('sub_menu', NavSubMenu()),
    ])
