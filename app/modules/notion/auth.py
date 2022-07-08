# stdlib
import os

# 3rd party
from consoler import console
from notion_client import Client


try:
    import envkey  # NOQA
except Exception:
    console.warn("No EnvKey / .env file found - running anyway")


# Ensure we have a token
TOKEN: str = os.environ.get('NOTION_WAGTAIL_TOKEN', '')


def get_notion_client():
    if not len(TOKEN):
        console.error("No token found. Add the NOTION_WAGTAIL_TOKEN to EnvKey")
    client = Client(auth=TOKEN)
    return client
