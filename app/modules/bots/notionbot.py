"""
    modules.bots.notionbot
    ~~~~~~~~~~~~~~~~~~~~~~
    A bot for sending notifications about the status of our Notion sync.
"""

from django.conf import settings
from .wagbot import WagBot


class NotionBot(WagBot):

    """Posts notion related messages to Slack
    """

    def __init__(self):
        super().__init__()
        self.channel = "#notion"
        self.username = "NotionBot"
        self.hook = settings.SLACK_HOOK_NOTIONBOT


notionbot = NotionBot()
