from consoler import console
from typing import Optional
from notion_client.client import Client


def get_page_id(url: str) -> str:
    """Takes a Notion Page url and tries to get a UUID.

    https://www.notion.so/hactar/Scope-44cf4bfd58844394bcfa26021dfb796b

    becomes

    44cf4bfd-5884-4394-bcfa-26021dfb796b

    Args:
        url (str): Description
    """
    unseparated = url.split('-')[-1]
    id_list = list(unseparated)
    id_list.insert(8, '-')
    id_list.insert(13, '-')
    id_list.insert(18, '-')
    id_list.insert(23, '-')
    id = ''.join(id_list)
    return id


def check_page_access(client: Client, page_id: str) -> bool:
    try:
        client.blocks.children.list(block_id=page_id)
    except Exception as e:
        console.error(e)
        console.error('Failed to get page. Did you "Share" the page with the Wagtail integration?')
        return False
    return True


def find_db_id(client: Client, page_id: str, db_name: str) -> Optional[str]:
    try:
        blocks: dict = client.blocks.children.list(block_id=page_id)
        for block in blocks['results']:
            if block['type'] == 'child_database':
                if _check_db_name(block, db_name):
                    return block['id']
        return None
    except Exception as e:
        console.error(e)
        console.error("Failed to find database or page")
        return None


def _check_db_name(block: dict, db_name: str) -> bool:
    try:
        if block['child_database']['title'] == db_name:
            return True
    except Exception as e:
        console.warn(e)
        return False

    return False
