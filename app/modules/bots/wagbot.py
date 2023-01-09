"""
    modules.bots.wagbot
    ~~~~~~~~~~~~~~~~~~~
    A Wagtail -> Slack notification bot - extend this to have different bots doing different
    jobs and sending to different channels etc.
"""

import json
import requests
from django.conf import settings
from consoler import console  # NOQA

import logging
logger = logging.getLogger(__name__)


class WagBot(object):

    """Base bot for posting messages to Slack.
    """

    def __init__(self):
        self.channel = "#general"
        self.username = "Wagbot"
        self.success_emoji = ":tada:"
        self.fail_emoji = ":thinking_face:"
        self.success_prefix = ""
        self.fail_prefix = ""
        self.hook = settings.SLACK_HOOK_WAGBOT

    def post(self, subject:str, message:str, success:bool = True):
        if success is True:
            emoji = self.success_emoji
            subject = f"{self.success_prefix}{subject}"
        else:
            emoji = self.fail_emoji
            subject = f"{self.fail_prefix}{subject}"
        try:
            body = f"""{emoji} *{subject}*\n{message}"""
            payload = {
                "username": self.username,
                "icon_emoji": emoji,
                "channel": self.channel,
                "text": body
            }
            data = json.dumps(payload)
            rv = requests.post(self.hook, data=data)  # NOQA
        except Exception as e:
            logger.warn('failed to post to slack')
            logger.warn(e)
            if rv in vars():
                logger.warn(rv)

    def success(self, subject:str, message:str):
        if settings.DEBUG:
            console.success(f'{self.username}: {subject}\n{message}')
        else:
            self.post(subject, message, True)

    def fail(self, subject:str, message:str):
        if settings.DEBUG:
            console.info(f'{self.username}: {subject}\n{message}')
        else:
            self.post(subject, message, False)
