from django.conf import settings
from wagtail import blocks


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
