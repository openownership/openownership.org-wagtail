import arrow
from datetime import datetime
from consoler import console
from django.db.models import Model
from django_cron import CronJobBase, Schedule
from modules.notion.data import COUNTRY_TRACKER, COMMITMENT_TRACKER, DISCLOSURE_REGIMES
from modules.notion.auth import get_notion_client
from modules.notion.utils import find_db_id
from modules.notion.models import CountryTag


DEFAULT_DATE = arrow.get('1970-01-01').datetime


class NotionCronBase(CronJobBase):

    def __init__(self, *args, **kwargs):
        self.client = get_notion_client()

    def _set_universals(self, obj: Model, data: dict) -> bool:
        """Sets the fields that are universal to our Notion model

        Args:
            obj (dict): The object we're currently handling.

        Returns:
            bool: Whether it succeeded or not
        """
        try:
            obj.notion_created = self._get_created(data)
            obj.notion_updated = self._get_updated(data)
            obj.archived = data.get('archived', False)
        except Exception as e:
            console.warn(e)
            return False
        else:
            return True

    def _get_created(self, data: dict) -> datetime:
        """Used for the notion_created datetime.
        We get this from data['created_time']

        Args:
            date_str (str): Description
        """
        date_str = data.get('created_time', '1970-01-01')
        try:
            return arrow.get(date_str).datetime
        except Exception as e:
            console.warn(e)
            return DEFAULT_DATE

    def _get_updated(self, data: dict) -> bool:
        """Used for the notion_updated datetime.
        We get this from data['last_edited_time']

        Args:
            date_str (str): Description
        """
        date_str = data.get('last_edited_time', '1970-01-01')
        try:
            return arrow.get(date_str).datetime
        except Exception as e:
            console.warn(e)
            return DEFAULT_DATE

    def _get_select_name(self, data: dict, property_name: str) -> str:
        """A select in Notion presents like this, we just want the name key

        'properties': {
            'OO Support': {
                'id': '%25%24OQ',
                'type': 'select',
                'select': {
                    'id': '9f7d1bc6-24f8-4e61-9581-a9b4ac649f7c',
                    'name': 'Medium',
                    'color': 'orange'
                }
            }
        }

        Args:
            data (dict): The dict we're grabbing the name from
        """
        try:
            return data['properties'][property_name]['select']['name']
        except Exception as e:
            console.warn(e)
            return ''


class SyncCountries(NotionCronBase):
    RUN_EVERY_MINS = 120  # every 2 hours

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'notion.sync_countries'

    def do(self, data: dict = None):
        """Sync countries from Notion

        Args:
            data (dict, optional): We're only going to pass the data in here in tests
        """
        # Find the countries DB
        db_id = find_db_id(self.client, COUNTRY_TRACKER, 'Country Tracker')
        if not data:
            data = self.client.databases.query(database_id=db_id)

        results = data.get('results', [])
        if len(results):
            # Do stuff here to save the data from Notion
            for item in results:
                self._handle_country(item)
        else:
            # Notify of failure, probably Slack and logging
            console.warn("Results was zero len")

    def _handle_country(self, country: dict) -> bool:
        try:
            notion_id = country['id']
        except KeyError:
            console.warn(country)
            console.error("No notion ID found")

        obj, created = CountryTag.objects.get_or_create(notion_id=notion_id)
        try:
            _notion_updated = country.get('last_edited_time')
            last_updated = arrow.get(_notion_updated).datetime
            our_updated = obj.notion_updated
        except Exception:
            console.error(f"Failed to get updated datetime from {_notion_updated}")
            last_updated = DEFAULT_DATE
            our_updated = obj.notion_updated
        if our_updated is not None and last_updated <= our_updated:
            # This row hasn't been updated since we last saved, so we can skip
            return False
        # This is either a new row, or it has been updated, so save stuff
        country_name = self._get_country_name(country)
        if country_name:
            obj.name = country_name
            self._set_universals(obj, country)
            try:
                obj.icon = country['icon']['emoji']
            except Exception:
                obj.icon = ''

            obj.oo_support = self._get_select_name(country, 'OO Support')

            obj.save()

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
            console.warn("Failed to get country name")
            console.warn(e)
            import ipdb; ipdb.set_trace()
            return ''


class SyncCommitments(NotionCronBase):
    RUN_EVERY_MINS = 120  # every 2 hours

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'notion.sync_commitments'

    def do(self, data: dict = None):
        """Sync commitments from Notion

        Args:
            data (dict, optional): We're only going to pass the data in here in tests
        """
        # The ID we have for COMMITMENT_TRACKER is already the DB id
        if not data:
            data = self.client.databases.query(database_id=COMMITMENT_TRACKER)
        # import ipdb; ipdb.set_trace()
        # Do stuff here to save the data from Notion


class SyncRegimes(NotionCronBase):
    RUN_EVERY_MINS = 120  # every 2 hours

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'notion.sync_regimes'

    def do(self, data: dict = None):
        """Sync regimes from Notion

        Args:
            data (dict, optional): We're only going to pass the data in here in tests
        """
        # The ID we have for DISCLOSURE_REGIMES is already the DB id
        if not data:
            data = self.client.databases.query(database_id=DISCLOSURE_REGIMES)
        # import ipdb; ipdb.set_trace()
        # Do stuff here to save the data from Notion
