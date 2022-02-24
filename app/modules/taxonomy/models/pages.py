

class DummyPage(object):
    """
    A fake Page.

    Sometimes we want to pass one or more Things to the templates, perhaps
    for display as cards, but they're not actually Pages. But the template
    expects Pages.
    So, we can use this class to make a fake Page with expected properties
    so that the template can render the data easily.

    e.g.
        page = DummyPage()
        page.title = "Bob's page"
        page.url = '/users/bob/'

    I know, it seems crazy.
    """

    pk = None
    title = ''
    url = ''
    blurb = ''

    def get_url(self):
        return self.url

    @property
    def specific(self):
        return self
