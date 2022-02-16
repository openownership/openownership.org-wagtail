from django.conf import settings
from wagtail.core import blocks


class SocialMediaItem(blocks.StructBlock):

    class Meta:
        icon = 'fa-connectdevelop'
        label = "Social media account"

    service = blocks.ChoiceBlock(
        choices=[
            (choice.lower(), choice) for choice in settings.SOCIAL_MEDIA_CHOICES
        ],
        required=True
    )

    url = blocks.URLBlock(required=True)
