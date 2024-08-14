# 3rd party
from loguru import logger
from django.conf import settings
from django_cron import Schedule
from django.template.defaultfilters import slugify

# Module
from modules.notion.helpers import check_headers
from modules.notion.data import COUNTRY_TRACKER
from modules.notion.models import CountryTag
from modules.notion.cron.core import NotionCronBase


class SyncCountries(NotionCronBase):
    RUN_EVERY_MINS = 120  # every 2 hours

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'notion.sync_countries'

    def __init__(self, *args, **kwargs):
        self._model = CountryTag
        super().__init__(*args, **kwargs)

    def do(self, data: dict = None, force: bool = False):
        """Sync countries from Notion

        Args:
            data (dict, optional): We're only going to pass the data in here in tests
            force (bool, optional): Force this to run
        """
        # The ID we have for COUNTRY_TRACKER is already the DB id
        if not data:
            data = self.fetch_all_data(COUNTRY_TRACKER)

        if check_headers("Country", data):
            self._process_data(data, force)
            self._clean_up(data)


    def _process_data(self, data: dict, force: bool = False) -> bool:
        results = data.get('results', [])
        if len(results):
            # Do stuff here to save the data from Notion
            for item in results:
                self._handle_country(item, force)
        else:
            # Notify of failure, probably Slack and logging
            logger.warning("Countries - Results was zero len")

    def _handle_country(self, country: dict, force: bool = False) -> bool:
        """Gets data from notion (`country`) and saves it as a Country tag.

        Args:
            country (dict): The OG Notion data, as a dict for a single country

        Returns:
            bool: Success / Failure
        """
        # Before we start trying to create the countries, we need to delete any countries
        # that may exist with a blank name field from empty rows in the Notion
        CountryTag.objects.filter(name='').all().delete()

        # OK, now we're ready
        try:
            notion_id = country['id']
        except KeyError:
            logger.warning(country)
            logger.error("No notion ID found")

        country_name = self._get_country_name(country)

        logger.info(f"Country name: {country_name}")

        if not country_name:
            return False

        try:
            obj, created = CountryTag.objects.get_or_create(notion_id=notion_id)
        except Exception as err:
            logger.warning(err)
            logger.log(country)
            breakpoint()

        logger.info(f"Country: {obj.notion_id} - Created: {created}")

        if not self._is_updated(obj, country) and not force:
            return False

        # This is either a new row, or it has been updated, so save stuff

        if country_name:
            obj.name = country_name
            obj.slug = slugify(country_name)
            self._set_universals(obj, country)
            try:
                obj.icon = country['icon']['emoji']
            except Exception:
                obj.icon = ''

            obj.oo_support = self._get_select_name(country, 'OO Support')
            obj.iso2 = self._get_plain_text(country, 'ISO2')

            try:
                obj.save()
            except Exception as e:
                logger.error("Failed to save")
                logger.error(e)
                # if settings.DEBUG:
                    # import ipdb; ipdb.set_trace()  # noqa: E702
        else:
            logger.warning("No country name found")
            return False

    def _get_country_name(self, data: dict) -> str:
        """
        Country name presents like this, we just want the plain_text...

        'properties': {
            'Country': {
                'id': 'title',
                'type': 'title',
                'title': [
                    {
                        'type': 'text',
                        'text': {
                            'content': 'Afghanistan',
                            'link': None
                        },
                        'annotations': {
                            'bold': False,
                            'italic': False,
                            'strikethrough': False,
                            'underline': False,
                            'code': False,
                            'color': 'default'
                        },
                        'plain_text': 'Afghanistan',
                        'href': None
                    }
                ]
            }
        }
        """
        try:
            return data['properties']['Country']['title'][0]['plain_text']
        except Exception as e:
            logger.warning("Failed to get country name")
            logger.warning(e)
            logger.warning(data)
            return ''
