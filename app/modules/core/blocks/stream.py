"""
    blocks.stream
    ~~~~~~~~~~~~~
    Primary stream blocks.
"""

# 3rd party
from wagtail.embeds import embeds
from wagtail.embeds.blocks import EmbedBlock as WagtailEmbedBlock

# Module
from .mixins import (  # NOQA
    TitleMixin, EyebrowMixin, CTAStreamBlock, TitleBodyMixin, EyebrowTitleMixin,
    EyebrowTitleBodyMixin
)
from .generic import CTABlock, CardStreamBlock  # NOQA


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
