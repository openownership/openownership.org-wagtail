"""
    blocks.stream
    ~~~~~~~~~~~~~
    Primary stream blocks.
"""

from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from wagtail.core import blocks

from wagtail.embeds import embeds
from wagtail.embeds.blocks import EmbedBlock as WagtailEmbedBlock

from wagtail.images.blocks import ImageChooserBlock

from wagtail.snippets.blocks import SnippetChooserBlock

# Module
from .mixins import (  # NOQA
    TitleMixin, EyebrowMixin, CTAStreamBlock, TitleBodyMixin, EyebrowTitleMixin,
    EyebrowTitleBodyMixin
)

from .generic import LinkBlock, CTABlock, CardStreamBlock  # NOQA


####################################################################################################
# Glossary
####################################################################################################

class GlossaryItemBlock(blocks.StructBlock):

    class Meta:
        label = 'Glossary item'
        icon = 'fa-help'
        template = 'blocks/glossary_item.jinja'

    title = blocks.CharBlock(required=True)
    body = blocks.RichTextBlock(
        required=True,
        features=settings.RICHTEXT_INLINE_FEATURES
    )


####################################################################################################
# Embeds
####################################################################################################

class EmbedBlockMixin(WagtailEmbedBlock):

    def get_context(self, value, parent_context={}):
        context = super().get_context(value, parent_context=parent_context)
        request = parent_context.get('request')
        third_party_cookies = request.COOKIES.get('third_party_cookies', 'acccept')

        embed_url = getattr(value, 'url', None)
        if embed_url:
            embed = embeds.get_embed(embed_url)
            context['embed_html'] = embed.html
            context['embed_url'] = embed_url
            context['ratio'] = embed.ratio

        context['third_party_cookies'] = third_party_cookies
        return context


class EmbedBlock(EmbedBlockMixin):
    class Meta:
        label = 'Embed'
        icon = 'media'
        template = "blocks/embed.jinja"


####################################################################################################
# Notifications / update banners
####################################################################################################

class NotificationBlock(blocks.StructBlock):

    class Meta:
        icon = 'fa-bell-o'
        template = 'blocks/notification.jinja'

    body = blocks.RichTextBlock(
        required=True,
        help_text="Body text",
        features=settings.RICHTEXT_INLINE_FEATURES
    )

    cta = CTABlock(required=True)


####################################################################################################
# Steps
####################################################################################################

class _StepsBlockItem(blocks.StructBlock):

    body = blocks.RichTextBlock(
        required=True,
        features=settings.RICHTEXT_INLINE_FEATURES
    )


class StepsBlock(TitleMixin):

    class Meta:
        icon = 'fa-sort-numeric-asc'
        template = 'blocks/steps.jinja'

    objects = blocks.ListBlock(
        _StepsBlockItem(required=True)
    )
    cta = CTABlock(required=False)


####################################################################################################
# Social media
####################################################################################################


class SocialMediaBlock(TitleBodyMixin):

    class Meta:
        label = 'Share banner'
        icon = 'fa-share-alt'
        template = "blocks/social_media.jinja"


####################################################################################################
# Icon list
####################################################################################################


class _IconListBlockItem(blocks.StructBlock):

    icon = blocks.ChoiceBlock(
        choices=settings.ICON_CHOICES,
        required=False
    )

    title = blocks.CharBlock(required=True)
    body = blocks.RichTextBlock(
        required=False,
        features=settings.RICHTEXT_INLINE_FEATURES
    )


class IconListBlock(blocks.StructBlock):

    class Meta:
        template = 'blocks/features_list.jinja'
        label = 'Features list'
        icon = 'fa-font-awesome'

    objects = blocks.ListBlock(_IconListBlockItem(), label="Blocks", required=True)


####################################################################################################
# Stats
####################################################################################################

class _StatBlock(blocks.StructBlock):

    """Add a stat, with Image, Text and CTA

    Attributes:
        image (ImageChooserBlock): The image to show
    """

    stat_text = blocks.CharBlock(
        required=True,
        help_text="Text version of this stat"
    )

    description = blocks.CharBlock(
        max_length=255,
        required=False
    )


class StatsBlock(TitleBodyMixin):
    class Meta:
        label = 'Stats'
        icon = 'fa-external-link-square'
        template = "blocks/stats.jinja"

    objects = blocks.ListBlock(
        _StatBlock(
            required=True,
            label="Stat"
        ),
        required=True
    )


####################################################################################################
# Newsletter
####################################################################################################

class NewsletterBlock(blocks.StructBlock):
    class Meta:
        label = 'Newsletter signup'
        icon = 'fa-envelope'
        template = "blocks/newsletter.jinja"

    eyebrow = blocks.CharBlock(
        required=False,
        default="Newsletter"
    )

    title = blocks.CharBlock(
        required=False
    )

    intro = blocks.RichTextBlock(
        required=False,
        features=settings.RICHTEXT_INLINE_FEATURES
    )

    def get_context(self, value, parent_context={}):
        context = super().get_context(value, parent_context=parent_context)

        context.update({
            'title': value.get('title'),
            'intro': value.get('intro'),
        })

        return context


####################################################################################################
# Video panel
####################################################################################################

class EmbedBannerBlock(EyebrowTitleBodyMixin):

    class Meta:
        icon = 'fa-play-circle'
        template = "blocks/embed_banner.jinja"

    embed = EmbedBlock(required=True)
    image = ImageChooserBlock(required=True)

    layout = blocks.ChoiceBlock(
        choices=[
            ('left', 'Left'),
            ('right', 'Right'),
        ],
        required=True
    )

    def get_context(self, value, parent_context={}):
        context = super().get_context(value, parent_context=parent_context)
        request = parent_context.get('request')
        third_party_cookies = request.COOKIES.get('third_party_cookies', 'acccept')

        embed_url = getattr(value['embed'], 'url', None)
        if embed_url:
            embed = embeds.get_embed(embed_url)
            context['embed_html'] = embed.html
            context['embed_url'] = embed_url
            context['ratio'] = embed.ratio
            context['embed_id'] = embed.pk

        context['third_party_cookies'] = third_party_cookies
        return context


####################################################################################################
# Video gallery
####################################################################################################

class _VideoGalleryItem(blocks.StructBlock):

    title = blocks.CharBlock(required=True)
    embed = EmbedBlock(required=True)
    image = ImageChooserBlock(required=True)


class VideoGalleryBlock(blocks.StructBlock):
    class Meta:
        icon = 'fa-quote-left'
        template = 'blocks/video_gallery.jinja'

    objects = blocks.ListBlock(
        _VideoGalleryItem,
        required=True,
        label="Videos"
    )


####################################################################################################
# Quotes
####################################################################################################

class PullQuoteBlock(blocks.StructBlock):
    class Meta:
        icon = 'fa-quote-left'
        template = 'blocks/pull_quote.jinja'

    quote = blocks.TextBlock(required=True)


class BlockQuoteBlock(blocks.StructBlock):
    class Meta:
        icon = 'fa-indent'
        template = 'blocks/block_quote.jinja'

    quote = blocks.TextBlock(required=True)


####################################################################################################
# Logo list
####################################################################################################

class _LogoListItem(blocks.StructBlock):

    class Meta:
        label = 'Logo item'
        icon = 'fa-pied-piper'

    image = ImageChooserBlock(required=True)
    url = blocks.URLBlock(required=False)


class LogoListBlock(EyebrowTitleBodyMixin):
    class Meta:
        label = 'Logo list'
        icon = 'fa-pied-piper'
        template = "blocks/logo_list.jinja"

    objects = blocks.ListBlock(
        _LogoListItem(required=True, label="Logo"),
        required=True,
        label="Logos"
    )


####################################################################################################
# Banner
####################################################################################################

class BannerBlock(EyebrowTitleMixin):
    class Meta:
        icon = 'fa-minus'
        template = 'blocks/banner.jinja'

    cta = CTABlock(required=False)


####################################################################################################
# News blocks
####################################################################################################

def get_news_category_choices():
    from modules.content.models import NewsCategory
    return NewsCategory.objects.values_list('id', 'name')


class LatestNewsBlock(TitleMixin):

    class Meta:
        icon = 'fa-newspaper-o'
        template = "blocks/news_listing.jinja"

    DEFAULT_LIMIT = 4
    limit_number = blocks.IntegerBlock(required=True, default=DEFAULT_LIMIT)
    limit_to_categories = blocks.MultipleChoiceBlock(
        choices=get_news_category_choices,
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    def get_context(self, value, parent_context={}):
        from modules.content.models import NewsArticlePage
        context = super().get_context(value, parent_context=parent_context)

        query = NewsArticlePage.objects.live()

        categories = value.get('limit_to_categories')

        if categories:
            query = query.filter(categories__id__in=categories)

        objects = list(
            query.distinct().order_by('-display_date')[:value.get('limit', self.DEFAULT_LIMIT)]
        )

        context.update({
            'objects': objects,
            'highlight_first': True
        })

        return context


####################################################################################################
# Section content
####################################################################################################


class LatestSectionContentBlock(blocks.StructBlock):
    """
    The most recently published Articles, Blog Articles, News Articles or
    Publications that are descendants of a front section page.
    """

    class Meta:
        icon = 'fa-newspaper-o'
        template = "_partials/card_group.jinja"

    DEFAULT_LIMIT = 3

    section_page = blocks.PageChooserBlock(
        required=True,
        label="Front page of section",
        page_type=(
            'content.SectionPage',          # Insight, Impact, Implement
            # 'content.SectionListingPage',   # About
        )
    )

    def get_context(self, value, parent_context={}):
        from modules.content.models import ArticlePage, BlogArticlePage, NewsArticlePage, PublicationFrontPage

        context = super().get_context(value, parent_context=parent_context)

        section_page = value.get('section_page')

        if section_page:
            pages = (
                section_page.get_descendants()
                .live().public()
                .exact_type(
                    ArticlePage, BlogArticlePage, NewsArticlePage, PublicationFrontPage
                )
                .specific()
                .order_by('-first_published_at')[:self.DEFAULT_LIMIT]
            )

            context.update({
                'pages': pages,
                'title': _('Latest {}').format(section_page.title),
            })

        return context


####################################################################################################
# Card groups
####################################################################################################

class CardGroupBlock(TitleMixin):

    class Meta:
        label = 'Card group'
        icon = 'fa-th-large'
        template = "blocks/card_group.jinja"

    objects = CardStreamBlock(min_num=1, label="Cards")

    def get_context(self, value, parent_context={}):
        context = super().get_context(value, parent_context=parent_context)

        object_count = len(value.get('objects', []))

        context.update({
            'object_count': object_count
        })

        return context


####################################################################################################
# Text columns
####################################################################################################

class _TextColumnBlockItem(TitleBodyMixin):

    """An item with title, body, and CTA for use inside other blocks.
    """

    cta = CTABlock(required=False)


class TextColumnsBlock(blocks.StructBlock):

    """
        Multi-column bits.
    """
    class Meta:
        label = 'Text columns'
        icon = 'fa-columns'
        template = "blocks/text_columns.jinja"

    objects = blocks.ListBlock(
        _TextColumnBlockItem(required=True, label="Column"),
        required=True,
        label="Columns"
    )

    def get_context(self, value, parent_context={}):
        context = super().get_context(value, parent_context=parent_context)

        num_objects = 0
        if value.get('objects'):
            num_objects = len(value.get('objects'))

        context.update({
            'num_objects': num_objects
        })

        return context


####################################################################################################
# Form Assembly
####################################################################################################

class FormAssemblyBlock(blocks.StructBlock):

    class Meta:
        icon = 'fa-database'
        template = "blocks/formassembly.jinja"

    heading = blocks.CharBlock(
        required=False
    )

    intro = blocks.RichTextBlock(
        required=False,
        features=settings.RICHTEXT_INLINE_FEATURES
    )

    formassembly_form = SnippetChooserBlock('crm.FormAssemblyForm', required=True)

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        context['form_html'] = value.get('formassembly_form').cleaned_html
        return context
