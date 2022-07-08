# 3rd party
import click
from django.conf import settings
from utils.console import console
from django.utils.text import slugify
from wagtail.core.models import Page, Site

# Project
from modules.content.models.pages import HomePage


DEFAULT_PAGES: list = []

DEFAULT_TAXONOMY: list = []

PRIMARY_NAV_PAGES: dict = {}

FOOTER_NAV_PAGES: list = []

PRIMARY_NAV_HIGHLIGHT: str = ''


class Scaffold(object):

    def first_build(self):
        self._clear_initial_data()
        site = self._create_site()
        home = self._create_home_page(site)
        self._create_default_pages(home)
        self._create_taxonomy()

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

    def _create_taxonomy(self):
        for name, model in DEFAULT_TAXONOMY:
            model.objects.get_or_create(name=name)
