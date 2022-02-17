from consoler import console


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


def check_page_access(client, page_id):
    # console.info(f"Checking page access for {page_id}")
    try:
        client.blocks.children.list(block_id=page_id)
    except Exception as e:
        console.error(e)
        console.error('Failed to get page. Did you "Share" the page with the Wagtail integration?')
        return False
    return True
