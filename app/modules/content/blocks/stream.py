"""
    blocks.stream
    ~~~~~~~~~~~~~
    Primary stream blocks.
"""

# stdlib
from collections import Counter

# 3rd party
from django import forms
from consoler import console
from django.conf import settings
from wagtail import blocks
from wagtail.embeds import embeds
from wagtail.models import Page, Locale
from wagtail.embeds.blocks import EmbedBlock as WagtailEmbedBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.snippets.blocks import SnippetChooserBlock
from django.utils.translation import gettext_lazy as _
from wagtailmodelchooser.blocks import ModelChooserBlock
from wagtail.contrib.table_block.blocks import TableBlock

# Module
from .mixins import TitleMixin, TitleBodyMixin, EyebrowTitleMixin, EyebrowTitleBodyMixin  # NOQA
from .values import LatestBlogValue, LatestNewsValue, LatestContentValue, LatestPublicationsValue
from .generic import CTABlock, ArticleImageBlock


####################################################################################################
# Footnotes
####################################################################################################


class FootnoteBlock(blocks.StructBlock):

    """The template for these is blank because we don't actually want them
    to render inline in the stream.
    """

    class Meta:
        label = "Footnote"
        icon = "anchor"
        template = "blocks/footnote_block.jinja"

    anchor = blocks.CharBlock(
        max_length=50,
        help_text="""This is the anchor that you link to in your RichText.
            Try to make it URL-safe, using `-` characters instead of spaces and punctuation
            characters."""
    )
    body = blocks.RichTextBlock(
        required=False,
        features=['bold', 'italic', 'underline', 'small', 'link'],
        help_text="""Body for the footnote. Wherever you place this block in the stream, it
            will render at the foot of the page."""
    )


####################################################################################################
# Glossary
####################################################################################################

class GlossaryItemBlock(blocks.StructBlock):

    class Meta:
        label = 'Glossary item'
        icon = 'help'
        template = 'blocks/glossary_item.jinja'

    title = blocks.CharBlock(required=True)
    body = blocks.RichTextBlock(
        required=True,
        features=settings.RICHTEXT_INLINE_FEATURES
    )


####################################################################################################
# New taxonomy related blocks
####################################################################################################

class LatestBlogBlock(blocks.StructBlock):

    class Meta:
        label = 'Latest blog posts'
        icon = 'doc-full'
        template = "_partials/card_group.jinja"
        value_class = LatestBlogValue

    title = blocks.CharBlock(
        required=True,
        default="Latest blog posts"
    )
    section = ModelChooserBlock(
        'taxonomy.SectionTag',
        required=False,
        help_text=""
    )


class LatestNewsBlock(blocks.StructBlock):

    class Meta:
        label = 'Latest news'
        icon = 'doc-full'
        template = "_partials/card_group.jinja"
        value_class = LatestNewsValue

    title = blocks.CharBlock(
        required=True,
        default="Latest news"
    )
    section = ModelChooserBlock(
        'taxonomy.SectionTag',
        required=False,
        help_text=""
    )


class LatestPublicationsBlock(blocks.StructBlock):

    class Meta:
        label = 'Latest publications'
        icon = 'doc-full'
        template = "_partials/card_group.jinja"
        value_class = LatestPublicationsValue

    title = blocks.CharBlock(
        required=True,
        default="Latest publications"
    )
    section = ModelChooserBlock(
        'taxonomy.SectionTag',
        required=False,
        help_text=""
    )


class LatestContentBlock(blocks.StructBlock):

    class Meta:
        label = 'Latest content'
        icon = 'doc-full'
        template = "_partials/card_group.jinja"
        value_class = LatestContentValue
        help_text = "Shows latest blog posts, news and job pages"

    title = blocks.CharBlock(
        required=True,
        default="Latest"
    )
    section = ModelChooserBlock(
        'taxonomy.SectionTag',
        required=False,
        help_text=""
    )


####################################################################################################
# Related Content
####################################################################################################


class SimilarContentBlock(blocks.StructBlock):
    """
    Select from Areas of Focus, Sectors, Publication Types, or Authors,
    and then display 3 pages that share those attributes with the
    current Page.
    """

    class Meta:
        label = _('Similar Content')
        group = _('Card group')
        icon = 'doc-full'
        template = "_partials/card_group.jinja"

    options = [
        # ('focus_area', _('Area of Focus')),
        ('sector', _('Topic')),
        ('publication_type', _('Content Type')),
        ('author', _('Author')),
        ('country', _('Country')),
        ('section', _('Section')),
        ('principles', _('Open Ownership Principles')),
    ]

    suggest_by = blocks.ChoiceBlock(choices=options, required=True, default='focus_area')

    def _ranked_pages(self, all_ids, count=3, relevance=True):
        ranked_ids = Counter(all_ids).most_common()
        if relevance:
            ids = [element[0] for element in ranked_ids[:count]]
        else:
            ids = [element[0] for element in ranked_ids]
        objects = (
            Page.objects
            .live().public().filter(locale=Locale.get_active())
            .filter(id__in=ids).specific()
            .order_by('-first_published_at').all()
        )
        return objects[:count]

    @property
    def by_focus_area(self):
        """Get the latest 3 articles by FocusAreaTag.
        """
        all_ids = []
        for tag in self.page.areas_of_focus.all():
            for item in tag.focusarea_related_pages.all():
                if item.content_object.id != self.page.id:
                    all_ids.append(item.content_object.id)

        objects = self._ranked_pages(all_ids, 3)
        return objects

    @property
    def by_country(self):
        """Get the latest 3 articles by CountryTag.
        """
        all_ids = []
        for tag in self.page.countries.all():
            for item in tag.country_related_pages.all():
                if item.content_object.id != self.page.id:
                    all_ids.append(item.content_object.id)

        objects = self._ranked_pages(all_ids, 3, relevance=False)
        return objects

    @property
    def by_section(self):
        """Get the latest 3 articles by SectionTag.
        """
        all_ids = []
        for tag in self.page.sections.all():
            for item in tag.section_tag_related_pages.all():
                if item.content_object.id != self.page.id:
                    all_ids.append(item.content_object.id)

        objects = self._ranked_pages(all_ids, 3)
        return objects

    @property
    def by_principle(self):
        """Get the latest 3 articles by PrincipleTag.
        """
        all_ids = []
        for tag in self.page.principles.all():
            for item in tag.principle_related_pages.all():
                if item.content_object.id != self.page.id:
                    all_ids.append(item.content_object.id)

        objects = self._ranked_pages(all_ids, 3)
        return objects

    @property
    def by_sector(self):
        """Get the latest 3 articles by SectorTag.
        """
        all_ids = []
        if not hasattr(self.page, 'sectors'):
            return []
        for tag in self.page.sectors.all():
            for item in tag.sector_related_pages.all():
                if item.content_object.id != self.page.id:
                    all_ids.append(item.content_object.id)

        objects = self._ranked_pages(all_ids, 3)
        return objects

    @property
    def by_publication_type(self):
        """Get the latest 3 articles by PublicationType.
        """
        all_ids = []
        if self.page.publication_type:
            for page in self.page.publication_type.pages.all():
                if page.id != self.page.id:
                    all_ids.append(page.id)

        objects = self._ranked_pages(all_ids, 3)
        return objects

    @property
    def by_authors(self):
        """Get the latest 3 articles by Author
        """
        if not hasattr(self.page, 'authors'):
            return []

        all_ids = []
        for author in self.page.authors:
            pages = author.get_content_pages(num=3)
            all_ids = all_ids + [page.id for page in pages if page.id != self.page.id]

        objects = self._ranked_pages(all_ids, 3)
        return objects

    def objects(self, mode):
        if mode == 'focus_area':
            return self.by_focus_area
        if mode == 'sector':
            return self.by_sector
        if mode == 'publication_type':
            return self.by_publication_type
        elif mode == 'author':
            return self.by_authors
        elif mode == 'country':
            return self.by_country
        elif mode == 'section':
            return self.by_section
        elif mode == 'principle':
            return self.by_principle
        else:
            return []

    def get_context(self, value, parent_context={}):
        context = super().get_context(value, parent_context=parent_context)
        mode = value.get('suggest_by', None)
        try:
            self.page = parent_context['page']
        except Exception as e:
            console.warn("Couldn't find a page for SimilarContentBlock")
            console.warn(e)

        context['title'] = _('Related articles and publications')
        context['pages'] = self.objects(mode)
        context['card_format'] = 'landscape'
        context['columns'] = 1
        return context


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
        icon = 'bell'
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
        icon = 'order'
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
        icon = 'share-nodes'
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
        icon = 'font-awesome'

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
        icon = 'link-external'
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
        icon = 'mail'
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
        icon = 'media'
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
        icon = 'openquote'
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
        icon = 'openquote'
        template = 'blocks/pull_quote.jinja'

    quote = blocks.TextBlock(required=True)


# class BlockQuoteBlock(blocks.StructBlock):
#     class Meta:
#         icon = 'fa-indent'
#         template = 'blocks/block_quote.jinja'

#     quote = blocks.TextBlock(required=True)


####################################################################################################
# Summary box
####################################################################################################


class SummaryBoxBlock(blocks.StructBlock):
    class Meta:
        icon = 'doc-full-inverse'
        template = 'blocks/summary_box.jinja'
        label = "Summary / highlight box"

    text = blocks.RichTextBlock(
        required=True, features=settings.RICHTEXT_SUMMARY_FEATURES
    )


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
        icon = 'minus'
        template = 'blocks/banner.jinja'

    cta = CTABlock(required=False)


####################################################################################################
# News blocks
####################################################################################################


def get_news_category_choices():
    from modules.content.models import NewsCategory
    return NewsCategory.objects.values_list('id', 'name')


####################################################################################################
# Pages
####################################################################################################


class HighlightPagesBlock(blocks.StructBlock):
    """
    For choosing a few pages from ALL of the pages to highlight on a Home,
    Section page, or Article.
    """

    class Meta:
        label = _('Highlight pages')
        group = _('Card group')
        icon = 'doc-full'
        template = "_partials/card_group.jinja"

    FORMAT_LANDSCAPE = 'landscape'
    FORMAT_PORTRAIT = 'portrait'

    FORMAT_CHOICES = (
        (FORMAT_LANDSCAPE, _('Landscape')),
        (FORMAT_PORTRAIT, _('Portrait')),
    )

    title = blocks.CharBlock(
        required=False,
        help_text=_('e.g. “Examples of our work”, or leave empty')
    )

    pages = blocks.ListBlock(
        blocks.StructBlock([
            ('page', blocks.PageChooserBlock(required=True)),
            ('card_format', blocks.ChoiceBlock(
                required=True, choices=FORMAT_CHOICES, default=FORMAT_LANDSCAPE)),
            ('embed', EmbedBlock(
                required=False,
                help_text=_(
                    "Optional, replaces the page's image. Only appears if Card format is Landscape."
                )
            )),
        ]),
        min_num=1
    )

    def get_context(self, value, parent_context={}):
        context = super().get_context(value, parent_context=parent_context)

        # Put the pages into a list that's easy to pass to the card_group template.
        pages = []
        for struct_value in value.get('pages'):
            page = struct_value.get('page')
            page.specific.card_format = struct_value.get('card_format')
            embed_url = getattr(struct_value.get('embed'), 'url', None)
            if embed_url:
                embed = embeds.get_embed(embed_url)
                embed_dict = {
                    'embed_html': embed.html,
                    'embed_url': embed_url,
                    'ratio': embed.ratio,
                    'emebd_id': embed.pk,
                }
                page.specific.card_embed = embed_dict
            pages.append(page.specific)

        context.update({
            'title': value.get('title', ''),
            'pages': pages,
        })
        return context


####################################################################################################
# Latest section content
####################################################################################################


class LatestSectionContentBlock(blocks.StructBlock):
    """
    The most recently published Articles, Blog Articles, News Articles or
    Publications that are descendants of a front section page.
    """

    class Meta:
        label = _('Latest section content')
        group = _('Card group')
        icon = 'time'
        template = "_partials/card_group.jinja"

    DEFAULT_LIMIT = 3

    section_page = blocks.PageChooserBlock(
        required=True,
        label=_("Front page of section"),
        page_type=(
            'content.SectionPage',  # Research, Impact, Implement
        )
    )

    def get_context(self, value, parent_context={}):
        from modules.content.models import content_page_models

        context = super().get_context(value, parent_context=parent_context)

        section_page = value.get('section_page')

        if section_page:
            pages = (
                section_page.get_descendants()
                .live().public().filter(locale=Locale.get_active())
                .exact_type(*content_page_models)
                .specific()
                .order_by('-first_published_at')[:self.DEFAULT_LIMIT]
            )

            context.update({
                'pages': pages,
                'title': _('Latest {}').format(section_page.title),
                'card_format': 'portrait',
            })

        return context


####################################################################################################
# Latest by focus area tag
####################################################################################################


class LatestFocusAreaBlock(blocks.StructBlock):
    """
    The most recently published pages tagged on `focus_area`
    """

    class Meta:
        label = _('Latest by Focus Area')
        group = _('Card group')
        icon = 'tag'
        template = "_partials/card_group.jinja"

    DEFAULT_LIMIT = 3

    title = blocks.CharBlock(
        required=False,
        help_text=_('If blank, will use "Latest"')
    )

    focus_area = ModelChooserBlock(
        'taxonomy.FocusAreaTag',
        required=True,
    )

    def get_context(self, value, parent_context={}):
        from wagtail.models import Page
        context = super().get_context(value, parent_context=parent_context)

        focus_area = value.get('focus_area', None)
        title = value.get('title', None)

        if focus_area:
            page_ids = focus_area.focusarea_related_pages.values_list(
                'content_object_id', flat=True)

            pages = Page.objects.filter(
                id__in=page_ids).live().public().specific().order_by(
                '-first_published_at')[:self.DEFAULT_LIMIT]

            context.update({
                'pages': pages,
                'title': title or "Latest",
                'card_format': 'portrait',
            })

        return context


####################################################################################################
# Latest by sector tag
####################################################################################################


class LatestSectorBlock(blocks.StructBlock):
    """
    The most recently published pages tagged on `sector`
    """

    class Meta:
        label = _('Latest by Topic')
        group = _('Card group')
        icon = 'tag'
        template = "_partials/card_group.jinja"

    DEFAULT_LIMIT = 3

    title = blocks.CharBlock(
        required=False,
        help_text=_('If blank, will use "Latest"')
    )

    sector = ModelChooserBlock(
        'taxonomy.SectorTag',
        required=True,
    )

    def get_context(self, value, parent_context={}):
        from wagtail.models import Page
        context = super().get_context(value, parent_context=parent_context)

        sector = value.get('sector', None)
        title = value.get('title', None)

        if sector:
            page_ids = sector.sector_related_pages.values_list(
                'content_object_id', flat=True)

            pages = Page.objects.filter(
                id__in=page_ids).live().public().specific().order_by(
                '-first_published_at')[:self.DEFAULT_LIMIT]

            context.update({
                'pages': pages,
                'title': title or "Latest",
                'card_format': 'portrait',
            })

        return context


####################################################################################################
# Latest by publication type
####################################################################################################


class LatestPublicationTypeBlock(blocks.StructBlock):
    """
    The most recently published pages of `publication_type`
    """

    class Meta:
        label = _('Latest by Publication Type')
        group = _('Card group')
        icon = 'tag'
        template = "_partials/card_group.jinja"

    DEFAULT_LIMIT = 3

    title = blocks.CharBlock(
        required=False,
        help_text=_('If blank, will use "Latest"')
    )

    publication_type = ModelChooserBlock(
        'taxonomy.PublicationType',
        required=True,
    )

    def get_context(self, value, parent_context={}):
        context = super().get_context(value, parent_context=parent_context)

        publication_type = value.get('publication_type', None)
        title = value.get('title', None)

        if publication_type:
            pages = publication_type.pages.live().public().specific().order_by(
                '-first_published_at')[:self.DEFAULT_LIMIT]

            context.update({
                'pages': pages,
                'title': title or "Latest",
                'card_format': 'portrait',
            })

        return context


####################################################################################################
# Latest by section tag
####################################################################################################


class LatestSectionTagBlock(blocks.StructBlock):
    """
    The most recently published pages of tagged with SectionTag
    """

    class Meta:
        label = _('Latest by Section Tag')
        group = _('Card group')
        icon = 'tag'
        template = "_partials/card_group.jinja"

    DEFAULT_LIMIT = 3

    title = blocks.CharBlock(
        required=False,
        help_text=_('If blank, will use "Latest"')
    )

    section = ModelChooserBlock(
        'taxonomy.SectionTag',
        required=True,
    )

    def get_context(self, value, parent_context={}):
        from wagtail.models import Page
        context = super().get_context(value, parent_context=parent_context)

        section = value.get('section', None)
        title = value.get('title', None)

        if section:
            page_ids = section.section_tag_related_pages.values_list(
                'content_object_id', flat=True)

            pages = Page.objects.filter(
                id__in=page_ids).live().public().specific().order_by(
                '-first_published_at')[:self.DEFAULT_LIMIT]

            context.update({
                'pages': pages,
                'title': title or "Latest",
                'card_format': 'portrait',
            })

        return context


####################################################################################################
# Latest by principle tag
####################################################################################################


class LatestPrincipleTagBlock(blocks.StructBlock):
    """
    The most recently published pages tagged with PrincipleTag
    """

    class Meta:
        label = _('Latest by Open Ownership Principle')
        group = _('Card group')
        icon = 'tag'
        template = "_partials/card_group.jinja"

    DEFAULT_LIMIT = 3

    title = blocks.CharBlock(
        required=False,
        help_text=_('If blank, will use "Latest"')
    )

    principle = ModelChooserBlock(
        'taxonomy.PrincipleTag',
        required=True,
    )

    def get_context(self, value, parent_context={}):
        from wagtail.models import Page
        context = super().get_context(value, parent_context=parent_context)

        principle = value.get('principle', None)
        title = value.get('title', None)

        if principle:
            page_ids = principle.principle_tag_related_pages.values_list(
                'content_object_id', flat=True)

            pages = Page.objects.filter(
                id__in=page_ids).live().public().specific().order_by(
                '-first_published_at')[:self.DEFAULT_LIMIT]

            context.update({
                'pages': pages,
                'title': title or "Latest",
                'card_format': 'portrait',
            })

        return context


####################################################################################################
# Taxonomies
####################################################################################################


class AreasOfFocusBlock(blocks.StructBlock):
    """
    For displaying blocks that link to taxonomy.views.FocusAreaPagesView pages.

    Choose tag(s) and display a card about each one, linking to its page.

    For Areas of Focus within a section (Impact, Research, Implement)
    """

    class Meta:
        label = _('Areas of focus')
        group = _('Card group')
        icon = "tag"
        template = "_partials/card_group.jinja"

    DEFAULT_LIMIT = 3
    DEFAULT_TITLE = 'Areas of Focus'

    FORMAT_LANDSCAPE = 'landscape'
    FORMAT_PORTRAIT = 'portrait'

    FORMAT_CHOICES = (
        (FORMAT_LANDSCAPE, _('Landscape')),
        (FORMAT_PORTRAIT, _('Portrait')),
    )

    title = blocks.CharBlock(
        required=False,
        help_text=_('Leave empty to use default: "{}"'.format(DEFAULT_TITLE))
    )

    card_format = blocks.ChoiceBlock(
        required=True, choices=FORMAT_CHOICES, default=FORMAT_LANDSCAPE
    )

    tags = blocks.ListBlock(
        ModelChooserBlock(
            'taxonomy.FocusAreaTag',
            required=True,
        ),
        min_num=1,
        max_num=DEFAULT_LIMIT,
        label=DEFAULT_TITLE,
    )

    def get_context(self, value, parent_context={}):
        context = super().get_context(value, parent_context=parent_context)

        # This will presumably be the Research SectionPage or similar:
        # (we need it to generate a URL to the tag page below this page)
        parent_page = parent_context['page']

        pages = []
        for tag in value.get('tags'):
            pages.append(tag.to_dummy_page(parent_page))

        context.update({
            'title': value.get('title') or self.DEFAULT_TITLE,
            'pages': pages,
            'card_format': value.get('card_format'),
        })

        return context


class SectorsBlock(AreasOfFocusBlock):
    """
    For displaying blocks that link to taxonomy.views.SectorPagesView pages.

    Choose tag(s) and display a card about each one, linking to its page.

    For Sectors within a section (Impact, Research, Implement)
    """

    class Meta:
        label = _('Topics')
        group = _('Card group')
        icon = "tag"
        template = "_partials/card_group.jinja"

    DEFAULT_LIMIT = 3
    DEFAULT_TITLE = 'Topics'

    title = blocks.CharBlock(
        required=False,
        help_text=_('Leave empty to use default: "{}"'.format(DEFAULT_TITLE))
    )

    tags = blocks.ListBlock(
        ModelChooserBlock(
            'taxonomy.SectorTag',
            required=True,
        ),
        min_num=1,
        max_num=DEFAULT_LIMIT,
        label=DEFAULT_TITLE,
    )


def get_publication_type_choices():
    from modules.taxonomy.models import PublicationType
    return PublicationType.objects.values_list('id', 'name')


class PublicationTypesBlock(blocks.StructBlock):
    """
    For displaying blocks that link to taxonomy.views.PublicationTypePagesView pages.

    Choose category/ies and display a card about each one, linking to its page.

    For Sectors within a section (Impact, Research, Implement)
    """

    class Meta:
        label = _('Publication types')
        group = _('Card group')
        icon = "doc-full"
        template = "_partials/card_group.jinja"

    DEFAULT_LIMIT = 3
    DEFAULT_TITLE = 'View by publication type'

    FORMAT_LANDSCAPE = 'landscape'
    FORMAT_PORTRAIT = 'portrait'

    FORMAT_CHOICES = (
        (FORMAT_LANDSCAPE, _('Landscape')),
        (FORMAT_PORTRAIT, _('Portrait')),
    )

    title = blocks.CharBlock(
        required=False,
        help_text=_(f'Leave empty to use default: "{DEFAULT_TITLE}"')
    )

    card_format = blocks.ChoiceBlock(
        required=True, choices=FORMAT_CHOICES, default=FORMAT_LANDSCAPE
    )

    types = blocks.MultipleChoiceBlock(
        choices=get_publication_type_choices,
        required=True,
        widget=forms.CheckboxSelectMultiple
    )

    def get_context(self, value, parent_context={}):
        from modules.taxonomy.models import PublicationType

        context = super().get_context(value, parent_context=parent_context)

        # This will presumably be the Research SectionPage or similar:
        # (we need it to generate a URL to the tag page below this page)
        parent_page = parent_context['page']

        pages = []
        for cat_type in value.get('types'):
            category = PublicationType.objects.get(pk=cat_type)
            pages.append(category.to_dummy_page())

        context.update({
            'title': value.get('title') or self.DEFAULT_TITLE,
            'pages': pages,
            'card_format': value.get('card_format'),
        })

        return context


####################################################################################################
# Press links
####################################################################################################


class PressLinksBlock(blocks.StructBlock):

    class Meta:
        label = _('Press links')
        group = _('Card group')
        icon = "doc-full"
        template = "_partials/card_group.jinja"

    DEFAULT_LIMIT = 3
    DEFAULT_TITLE = 'Press links'

    title = blocks.CharBlock(
        required=False,
        help_text=_(f'Leave empty to use default: "{DEFAULT_TITLE}"')
    )

    section = ModelChooserBlock(
        'taxonomy.SectionTag',
        required=False,
        help_text="Optional, restrict to press links tagged by section"
    )

    limit_number = blocks.IntegerBlock(required=True, default=DEFAULT_LIMIT)

    def get_context(self, value, parent_context={}):
        from modules.content.models import PressLink

        context = super().get_context(value, parent_context=parent_context)

        # This will presumably be the Research SectionPage or similar:
        # (we need it to generate a URL to the tag page below this page)
        # parent_page = parent_context['page']

        qs = PressLink.objects

        section = value.get('section', None)

        if section:
            related_snippets = section.section_tag_press_links.all()
            ids = [item.content_object_id for item in related_snippets]
            qs = qs.filter(id__in=ids)

        objects = qs.order_by("-first_published_at")[:value.get('limit', self.DEFAULT_LIMIT)]

        context.update({
            'title': value.get('title') or self.DEFAULT_TITLE,
            'pages': objects,
            'card_format': 'portrait',
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
        icon = 'clipboard-list'
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


####################################################################################################
# Details
####################################################################################################

class DisclosureBlock(blocks.StructBlock):
    "A title that, when clicked, reveals something else"

    class Meta:
        label = _('Details')
        icon = 'arrow-down'
        template = 'blocks/disclosure.jinja'

    title = blocks.CharBlock(required=True)

    body = blocks.StreamBlock([
        ('rich_text', blocks.RichTextBlock(features=settings.RICHTEXT_SUMMARY_FEATURES)),
        ('embed', EmbedBlock()),
        ('table', TableBlock()),
        ('image', ArticleImageBlock()),
    ], max_num=1)


####################################################################################################
# Search
####################################################################################################


class EditorsPicksBlock(blocks.StructBlock):
    """
    For choosing a few pages from ALL of the pages to highlight on a Home,
    Section page, or Article.
    """

    class Meta:
        label = _("Editor's picks")
        icon = 'doc-full'
        template = "_partials/search_stream.jinja"

    title = blocks.CharBlock(
        default="Editor's picks",
        required=False,
    )

    pages = blocks.ListBlock(
        blocks.StructBlock([
            ('page', blocks.PageChooserBlock(required=True)),
        ]),
        min_num=1, max_num=3
    )

    def get_context(self, value, parent_context={}):
        context = super().get_context(value, parent_context=parent_context)
        pages = []
        for struct_value in value.get('pages'):
            page = struct_value.get('page')
            pages.append(page.specific)

        context.update({
            'title': value.get('title', ''),
            'pages': pages,
        })
        value.pages = pages
        return context


class SearchLatestContentBlock(LatestContentBlock):

    class Meta:
        label = 'Latest content'
        icon = 'doc-full'
        template = "_partials/search_stream.jinja"
        value_class = LatestContentValue
        help_text = "Shows latest blog posts, news and job pages"
