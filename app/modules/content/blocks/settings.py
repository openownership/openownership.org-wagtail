# 3rd party
from django import forms
from wagtail import blocks
from django.conf import settings
from wagtail.documents.blocks import DocumentChooserBlock

# Module
from .mixins import CTABlockStructValue


class NavigationItem(blocks.StructBlock):
    class Meta:
        form_template = 'wagtail/cta_block_form.html'
        label = "Link"
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


class SubNavigationMenu(blocks.StructBlock):

    class Meta:
        label = 'Submenu'
        icon = 'bars'

    text = blocks.CharBlock(required=True)
    objects = blocks.ListBlock(
        NavigationItem()
    )


class TwoTieredNavigationMenu(blocks.StructBlock):

    objects = blocks.StreamBlock([
        ('nav_item', NavigationItem()),
        ('sub_nav', SubNavigationMenu()),
    ])


class SocialMediaItem(blocks.StructBlock):

    class Meta:
        icon = 'comment'
        label = "Social media account"

    service = blocks.ChoiceBlock(
        choices=[
            (choice.lower(), choice) for choice in settings.SOCIAL_MEDIA_CHOICES
        ],
        required=True
    )

    url = blocks.URLBlock(required=True)


single_tiered_navigation_menu_blocks = [
    ('nav_item', NavigationItem())
]


two_tiered_navigation_menu_blocks = [
    ('nav_item', NavigationItem()),
    ('sub_nav', SubNavigationMenu()),
]

social_media_blocks = [
    ('social_links', SocialMediaItem(required=True))
]
