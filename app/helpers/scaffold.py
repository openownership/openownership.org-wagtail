import click
from django.conf import settings
from django.utils.text import slugify

from wagtail.core.models import Site, Page
from helpers.console import console

from modules.core.models.pages import (
    LandingPage, ArticlePage, HomePage, SearchPage, SearchPageSuggestedSearch
)

from modules.core.models.navigation import (
    PrimaryNavigationMenu, PrimaryNavItem, PrimaryNavSubItem,
    FooterNavigationMenu, FooterNavItem
)

from modules.taxonomy.models import (
    PriorityAreaTag
)


DEFAULT_PAGES: list = [
    # ('About Esmée', LandingPage,
    #     [
    #         ('About us', LandingPage),
    #         ('Strategy', ArticlePage),
    #         ('Investments', ArticlePage),
    #         ('Open data', ArticlePage),
    #         ('Reports', LandingPage),
    #         ('News', NewsIndexPage),
    #         ('Funding strategy', LandingPage),
    #         ('Governance', LandingPage),
    #         ('Chief Executive\'s report', LandingPage),
    #         ('Our people', PeopleIndexPage)
    #     ]),
    # ('What we do', LandingPage,
    #     [
    #         ('Our natural world', LandingPage),
    #         ('A fairer future', LandingPage),
    #         ('Creative, confident communities', LandingPage),
    #     ]),
    # ('Our support', LandingPage, []),
    # ('Applications', ApplicationGuidancePage, []),
    # ('Partners', LandingPage, []),
    # ('Privacy policy', ArticlePage, []),
    # ('Search', SearchPage, [])
]


SUGGESTED_SEARCHES: list = [
    # ('url', '/quiz/', 'Take the Esmeé quiz'),
    # ('page', 'Applications', 'Guidance for applicants'),
]

PRIMARY_NAV_PAGES: dict = {
    # 'About Esmée': [
    #     'About us',
    #     'Strategy',
    #     'Investments',
    #     'Open data',
    #     'Reports',
    #     'News'
    # ],
    # 'What we do': [
    #     'Our natural world',
    #     'A fairer future',
    #     'Creative, confident communities'
    # ],
    # 'Our support': [],
    # 'Applications': [],
}

FOOTER_NAV_PAGES: list = [
    # 'About Esmée',
    # 'What we do',
    # 'Our support',
    # 'Applications',
    # 'Partners',
    # 'Privacy policy',
]

PRIMARY_NAV_HIGHLIGHT: str = ''  # 'Partners'


class Scaffold(object):

    def first_build(self):
        self._clear_initial_data()
        site = self._create_site()
        home = self._create_home_page(site)
        self._create_default_pages(home)
        self._create_nav_menus(site, purge=True)
        self._create_default_taxonomy()
        self._create_suggested_searches()

        console.info("SCAFFOLD COMPLETE")

    def _clear_initial_data(self):

        console.success('Done: _clear_initial_data')

    def _create_site(self):
        site = Site.objects.first()
        if site and site.site_name == settings.SITE_NAME:
            console.info('Skipping: _create_site')
            return site

        if not site:
            site = Site()

        site.site_name = settings.SITE_NAME
        site.hostname = settings.DOMAIN_NAME
        site.port = getattr(settings, 'SITE_PORT', 80)
        site.is_default_site = True
        site.save()
        console.success('Done: _create_site')
        return site

    def _create_home_page(self, site):

        if HomePage.objects.filter(slug="home").exists():
            console.info('Skipping: _create_home_page')
            return HomePage.objects.filter(slug="home").first()
        try:
            default_home = Page.objects.get(title="Welcome to your new Wagtail site!")
        except Page.DoesNotExist:
            home = HomePage.objects.first()
            if home:
                console.warn(f'Home page with title "{home.title}" and slug "{home.slug} exists')
                if click.confirm('Do you want to continue?', default=True):
                    return home
                raise Exception('Scaffold cancelled')

            else:
                raise Exception('No default page and no home page. Something is very wrong.')

        default_home.slug = "home-old"
        default_home.save_revision().publish()
        default_home.save()

        root_page = Page.objects.get(title="Root")

        home_page = root_page.add_child(
            instance=HomePage(
                title="Home",
                slug="home"
            )
        )

        home_page.save()
        revision = home_page.save_revision()
        revision.publish()

        site.root_page = home_page
        site.save()

        default_home.delete()

        console.success('Done: _create_home_page')
        return home_page

    def _create_default_pages(self, home_page):

        for title, Model, children in DEFAULT_PAGES:

            page = Page.objects.filter(title=title).first()
            if not page:
                page = home_page.add_child(
                    instance=Model(title=title, slug=slugify(title))
                )

            for child_title, ChildModel in children:
                if not Page.objects.filter(title=child_title).exists():
                    page.add_child(
                        instance=ChildModel(title=child_title, slug=slugify(child_title))
                    )

        console.info('Done: _create_default_pages')

    def _create_default_taxonomy(self):

        default_tags = [
            (PriorityAreaTag, [
                'Our natural world'
                'A fairer future',
                'Creative, confident communities'
            ]),
        ]

        for Model, tags in default_tags:
            for tag in tags:
                Model.objects.get_or_create(name=tag)

        console.info('Done: _create_default_taxonomy')

    def _process_nav_items(self, objects, nav_item_class=PrimaryNavItem):
        items = []

        for index, item in enumerate(DEFAULT_PAGES, 1):
            kwargs = {'sort_order': index}
            kwargs.update({
                'link_page': item[1].objects.get(title=item[0]),
                'text': item.get('text') or item.get('page')
            })

            items.append(nav_item_class(**kwargs))

        return items

    def _create_nav_menus(self, site, purge=False):

        primary_nav_pages = PRIMARY_NAV_PAGES

        footer_nav_pages = FOOTER_NAV_PAGES

        primary_nav_highlight = PRIMARY_NAV_HIGHLIGHT

        if purge:
            PrimaryNavSubItem.objects.all().delete()
            PrimaryNavItem.objects.all().delete()
            FooterNavItem.objects.all().delete()

        # Primary nav
        primary_nav = PrimaryNavigationMenu.objects.first()

        for index, item in enumerate(primary_nav_pages.items(), 1):
            title, children = item

            parent_page = Page.objects.get(title=title)

            parent_item, created = PrimaryNavItem.objects.get_or_create(
                link_page=parent_page,
                nav_menu=primary_nav,
                defaults={
                    'sort_order': index,
                    'text': title
                }
            )

            for child_index, child_title in enumerate(children, 1):
                child_page = Page.objects.get(
                    title=child_title,
                )

                PrimaryNavSubItem.objects.get_or_create(
                    link_page=child_page,
                    parent_id=parent_item.id,
                    defaults={
                        'sort_order': child_index,
                        'text': child_title
                    }
                )

        if primary_nav_highlight:
            primary_nav.highlighted_link_page = Page.objects.get(title=primary_nav_highlight)
            primary_nav.highlighted_item_text = primary_nav_highlight
            primary_nav.save()

        # Footer nav
        footer_nav = FooterNavigationMenu.objects.first()

        for index, title in enumerate(footer_nav_pages, 1):
            page = Page.objects.get(title=title)
            FooterNavItem.objects.get_or_create(
                link_page=page,
                nav_menu_id=footer_nav.id,
                defaults={
                    'sort_order': index,
                    'text': title
                }
            )

        console.info('Done: _create_nav_menus')

    def _create_suggested_searches(self):
        search_page = SearchPage.objects.first()

        for index, item in enumerate(SUGGESTED_SEARCHES, 1):
            link_type = item[0]
            link_text = item[2]

            if link_type == 'page':
                SearchPageSuggestedSearch.objects.get_or_create(
                    text=link_text,
                    search_page_id=search_page.id,
                    defaults={
                        'sort_order': index,
                        'link_page': Page.objects.get(title=item[1]),
                    }
                )

            if link_type == 'url':
                SearchPageSuggestedSearch.objects.get_or_create(
                    text=link_text,
                    search_page_id=search_page.id,
                    link_url=item[1],
                    defaults={
                        'sort_order': index,
                    }
                )
