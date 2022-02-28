from django.core.management import call_command

from modules.content.views import SearchView


def test_author_search(client, author_with_content_pages):
    """This doesn't do much currently as the search index on an SQLite DB doesn't
    seem to build properly.
    """
    # call_command('update_index')
    author = author_with_content_pages
    assert author.name == 'Bob Ferris'
    res = client.get('/en/search/?q=bob+ferris')
    assert res.status_code == 200
