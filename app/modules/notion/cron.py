import arrow
from typing import Optional
from datetime import datetime
from consoler import console
from django.db.models import Model
from django_cron import CronJobBase, Schedule
from modules.notion.data import COUNTRY_TRACKER, COMMITMENT_TRACKER, DISCLOSURE_REGIMES
from modules.notion.auth import get_notion_client
from modules.notion.models import CountryTag, Commitment, CoverageScope, DisclosureRegime


DEFAULT_DATE = arrow.get('1970-01-01').datetime


class NotionCronBase(CronJobBase):

    def __init__(self, *args, **kwargs):
        self.client = get_notion_client()

    def fetch_all_data(self, db_id: str) -> dict:
        self.has_more = False
        initial_data = self._fetch(db_id)
        data = initial_data
        self.has_more = data['has_more']
        try:
            while self.has_more is True:
                data = self._fetch(db_id, next_cursor=data['next_cursor'])
                initial_data['results'] += data['results']
                self.has_more = data['has_more']
        except KeyboardInterrupt:
            import ipdb; ipdb.set_trace()
        except Exception as e:
            console.error(e)
            import ipdb; ipdb.set_trace()
            raise

        return initial_data

    def _fetch(self, db_id: str, next_cursor: str = None):
        console.info(f"FETCH: {db_id} / {next_cursor}")
        data = self.client.databases.query(database_id=db_id, start_cursor=next_cursor)
        return data

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

    def _get_title(self, data: dict) -> str:
        """
        A Notion `Title` presents like this, we just want the plain_text...

        'properties': {
            'Title': {
                'id': 'title',
                'type': 'title',
                'title': [
                    {
                        'type': 'text',
                        'text': {
                            'content': 'Democratic Republic of the Congo EITI Register',
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
                        'plain_text': 'Democratic Republic of the Congo EITI Register',
                        'href': None
                    }
                ]
            }
        }
        """
        try:
            return data['properties']['Title']['title'][0]['plain_text']
        except Exception as e:
            console.warn("Failed to get Title")
            console.warn(e)
            return ''

    def _get_select_name(self, data: dict, property_name: str) -> Optional[str]:
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

        If there's nothing selected, it looks like this:

        'OO Support': {
            'id': '%25%24OQ',
            'type': 'select',
            'select': None
        }

        Args:
            data (dict): The dict we're grabbing the name from
        """
        if 'properties' not in data:
            import ipdb
            ipdb.set_trace()
        if property_name not in data['properties'].keys():
            return None
        try:
            if data['properties'][property_name]['select'] is not None:
                if 'name' in data['properties'][property_name]['select'].keys():
                    return data['properties'][property_name]['select']['name']
                else:
                    return None
        except Exception as e:
            console.warn(e)
            return None

    def _get_rel_id(self, data: dict, property_name: str) -> str:
        """A rel in Notion presents like this, we just want the relation id key

        'properties': {
            'Country': {
                'id': "X'sx",
                'type': 'relation',
                'relation': [
                    {
                        'id': 'be340a07-ee3d-44fe-8df1-98484fbda61c'
                    }
                ]
            }
        }

        Args:
            data (dict): The dict we're grabbing the name from
        """
        try:
            if len(data['properties'][property_name]['relation']):
                return data['properties'][property_name]['relation'][0]['id']
        except Exception as e:
            console.warn(e)
            return None

    def _get_plain_text(self, data: dict, property_name: str) -> str:
        """Get the plain text representation of a rich_text property in the Notion data

        'properties': {
            'Commitment type': {
                'id': ')UWR',
                'type': 'rich_text',
                'rich_text': [
                    {
                        'type': 'text',
                        'text': {
                            'content': 'Other',
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
                        'plain_text': 'Other',
                        'href': None
                    }
                ]
            }
        }

        Args:
            data (dict): The dict we're grabbing the str from
        """
        try:
            if len(data['properties'][property_name]['rich_text']):
                return data['properties'][property_name]['rich_text'][0]['plain_text']
        except Exception as e:
            console.warn(e)
            return ''

    def _get_rich_text(self, data: dict, property_name: str) -> str:
        """Get the rich text representation of a rich_text property in the Notion data.

        The only actual rich text we've found in the data is links, which is returned as
        below, we need to reconstruct the paragraph from this.

        'properties': {
            'Summary Text': {
                'id': 'ZC(N',
                'type': 'rich_text',
                'rich_text': [
                    {
                        'type': 'text',
                        'text': {
                            'content': 'Bahrain has made a commitment to beneficial ownership ',
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
                        'plain_text': 'Bahrain has made a commitment to beneficial ownership ',
                        'href': None
                    },
                    {
                        'type': 'text',
                        'text': {
                            'content': 'Ministerial Order No. (83) of 2020',
                            'link': {
                                'url': 'https://www.moic.gov.bh/en/Tiles/BusinessServices/'
                            }
                        },
                        'annotations': {
                            'bold': False,
                            'italic': False,
                            'strikethrough': False,
                            'underline': False,
                            'code': False,
                            'color': 'default'
                        },
                        'plain_text': 'Ministerial Order No. (83) of 2020',
                        'href': 'https://www.moic.gov.bh/en/Tiles/BusinessServices/Commercial'
                    }
                ]
            }
        }

        Args:
            data (dict): The dict we're grabbing the str from
        """
        try:
            result = ''
            for item in data['properties'][property_name]['rich_text']:
                if item['type'] == 'text' and item['text']['link'] is None:
                    result += f"{item['text']['content']}"
                elif item['type'] == 'text' and item['text']['link'] is not None:
                    url = item['text']['link']
                    linked_text = item['text']['content']
                    href = f'<a href="{url}">{linked_text}</a>'
                    result += href
            return result
        except Exception as e:
            console.warn(e)
            return ''

    def _get_url(self, data: dict, property_name: str) -> Optional[str]:
        """A url field in Notion presents like this, we just want the url key

        'properties': {
            'Link': {
                'id': '-ifl',
                'type': 'url',
                'url': 'https://www.imf.org/en/Publications/'
            },
        }

        Args:
            data (dict): The dict we're grabbing the name from
        """
        try:
            return data['properties'][property_name]['url']
        except Exception as e:
            console.warn(e)
            return None

    def _get_bool(self, data: dict, property_name: str) -> bool:
        """A checkbox / bool field in Notion presents like this, we just want the value

        'properties': {
            'Central register': {
                'id': 'o)_-',
                'type': 'checkbox',
                'checkbox': True
            }
        }

        Args:
            data (dict): The dict we're grabbing the name from
        """
        try:
            return data['properties'][property_name]['checkbox']
        except Exception as e:
            console.warn(e)
            return False

    def _get_date(self, data: dict, property_name: str) -> Optional[str]:
        """A date in Notion presents like this, we just want the start key

        'properties': {
            'Date': {
                'id': '%3Ao%7C%23',
                'type': 'date',
                'date': {
                    'start': '2022-02-04',
                    'end': None,
                    'time_zone': None
                }
            },
        }

        Args:
            data (dict): The dict we're grabbing the name from
        """
        try:
            if data['properties'][property_name]['date'] is not None:
                return data['properties'][property_name]['date']['start']
        except Exception as e:
            console.warn(e)
            return None

    def _is_updated(self, obj: Model, data: dict) -> bool:
        try:
            _notion_updated = data.get('last_edited_time')
            last_updated = arrow.get(_notion_updated).datetime
            our_updated = obj.notion_updated
        except Exception:
            console.error(f"Failed to get updated datetime from {_notion_updated}")
            last_updated = DEFAULT_DATE
            our_updated = obj.notion_updated
        if our_updated is not None and last_updated <= our_updated:
            # This row hasn't been updated since we last saved, so we can skip
            return False
        return True

    def _get_country(self, notion_id: str) -> CountryTag:
        """Looks up a CountryTag by notion_id

        Args:
            notion_id (str): The notion_id for the CountryTag we're looking for
        """
        # import ipdb; ipdb.set_trace()
        try:
            return CountryTag.objects.get(notion_id=notion_id)
        except Exception as e:
            console.warn(e)


class SyncCountries(NotionCronBase):
    RUN_EVERY_MINS = 120  # every 2 hours

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'notion.sync_countries'

    def do(self, data: dict = None):
        """Sync countries from Notion

        Args:
            data (dict, optional): We're only going to pass the data in here in tests
        """

        # The ID we have for COUNTRY_TRACKER is already the DB id
        if not data:
            data = self.fetch_all_data(COUNTRY_TRACKER)

        self._process_data(data)

    def _process_data(self, data: dict) -> bool:
        results = data.get('results', [])
        if len(results):
            # Do stuff here to save the data from Notion
            for item in results:
                self._handle_country(item)
        else:
            # Notify of failure, probably Slack and logging
            console.warn("Countries - Results was zero len")

    def _handle_country(self, country: dict) -> bool:
        """Gets data from notion (`country`) and saves it as a Country tag.

        Args:
            country (dict): The OG Notion data, as a dict for a single country

        Returns:
            bool: Success / Failure
        """
        try:
            notion_id = country['id']
        except KeyError:
            console.warn(country)
            console.error("No notion ID found")

        obj, created = CountryTag.objects.get_or_create(notion_id=notion_id)

        if not self._is_updated(obj, country):
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

            try:
                obj.save()
            except Exception as e:
                console.error("Failed to save")
                console.error(e)
                import ipdb; ipdb.set_trace()

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
            data = self.fetch_all_data(COMMITMENT_TRACKER)

        results = data.get('results', [])
        if len(results):
            # Do stuff here to save the data from Notion
            for item in results:
                self._handle_commitment(item)
        else:
            # Notify of failure, probably Slack and logging
            console.warn("Commitments - Results was zero len")

    def _handle_commitment(self, commitment: dict) -> bool:
        """Gets data from notion (`commitment`) and saves it as a Commitment.

        Args:
            commitment (dict): The OG Notion data, as a dict for a single commitment row

        Returns:
            bool: Success / Failure
        """
        # import ipdb; ipdb.set_trace()
        try:
            notion_id = commitment['id']
        except KeyError:
            console.warn(commitment)
            console.error("No notion ID found")

        country_id = self._get_rel_id(commitment, 'Country')
        if country_id is None:
            return False

        country = None
        if country_id:
            country = self._get_country(country_id)

        if country:
            obj, created = Commitment.objects.get_or_create(notion_id=notion_id, country=country)
        else:
            console.warn("No related country found, skipping")
            return False

        if not self._is_updated(obj, commitment):
            return False

        # This is either a new row, or it has been updated, so save stuff
        self._set_universals(obj, commitment)

        obj.oo_support = self._get_select_name(commitment, 'OO Support')
        obj.date = self._get_date(commitment, 'Date')
        obj.link = self._get_url(commitment, 'Link')
        obj.commitment_type_name = self._get_plain_text(commitment, 'Commitment type')
        obj.central_register = self._get_bool(commitment, 'Central register')
        obj.public_register = self._get_bool(commitment, 'Public register')
        obj.summary_text = self._get_rich_text(commitment, 'Summary Text')

        try:
            obj.save()
        except Exception as e:
            console.error("Failed to save")
            console.error(e)
            import ipdb; ipdb.set_trace()


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
            data = self.fetch_all_data(DISCLOSURE_REGIMES)

        results = data.get('results', [])
        if len(results):
            # Do stuff here to save the data from Notion
            for item in results:
                self._handle_regime(item)
        else:
            # Notify of failure, probably Slack and logging
            console.warn("Regimes - Results was zero len")

    def _handle_regime(self, regime: dict) -> bool:
        """Gets data from notion (`regime`) and saves it as a DisclosureRegime.

        Args:
            regime (dict): The OG Notion data, as a dict for a single regime row

        Returns:
            bool: Success / Failure
        """
        # import ipdb; ipdb.set_trace()
        try:
            notion_id = regime['id']
        except KeyError:
            console.warn(regime)
            console.error("No notion ID found")

        country_id = self._get_rel_id(regime, 'Country')
        if country_id is None:
            return False

        country = None
        if country_id:
            country = self._get_country(country_id)

        if country:
            obj, created = DisclosureRegime.objects.get_or_create(
                notion_id=notion_id,
                country=country
            )
        else:
            console.warn("No related country found, skipping")
            return False

        if not self._is_updated(obj, regime):
            return False

        # This is either a new row, or it has been updated, so save stuff
        self._set_universals(obj, regime)
        obj.title = self._get_title(regime)
        obj.definition_legislation_url = self._get_url(
            regime, '1.1 Definition: Legislation URL'
        )
        obj.coverage_legislation_url = self._get_url(
            regime, '2.3 Coverage: Legislation URL'
        )
        scope_tags = self._get_scope_tags(regime)
        if scope_tags:
            for item in scope_tags:
                obj.coverage_scope.add(item)
                obj.coverage_scope.commit()
        obj.central_register = self._get_select_name(regime, '4.1 Central register')
        obj.public_access = self._get_select_name(regime, '5.1 Public access')
        obj.public_access_register_url = self._get_url(regime, '5.1.1 Public access: Register URL')
        obj.year_launched = self._get_select_name(regime, '5.1.2 Year launched')
        obj.structured_data = self._get_select_name(regime, '6.1 Structured data')
        obj.api_available = self._get_select_name(regime, '6.3 API available')
        obj.data_in_bods = self._get_select_name(regime, '6.4 Data published in BODS')
        obj.on_oo_register = self._get_bool(regime, '6.5 Data on OO Register')
        obj.legislation_url = self._get_url(regime, '8.4 Legislation URL')

        try:
            obj.save()
        except Exception as e:
            console.error("Failed to save")
            console.error(e)
            import ipdb; ipdb.set_trace()

    def _get_scope_tags(self, data: dict) -> list:
        """Takes this dict, creates a CoverageScope tag for each `name` and returns a list of them

        '2.1 Coverage: Scope': {
            'id': 'Z%3Dqf',
            'type': 'multi_select',
            'multi_select': [
                {
                    'id': 'd084a8fc-fbbc-4d63-b184-b6ab5717e644',
                    'name': 'Full-economy',
                    'color': 'green'
                },
                {
                    'id': '859da0c6-cb5b-40f8-b238-8c7e913fb3e5',
                    'name': 'Sectoral: Extractives',
                    'color': 'purple'
                }
            ]
        }

        Args:
            data (dict): The disclosure regime row

        Returns:
            list: List of tags
        """
        try:
            tags = []
            scopes = data['properties']['2.1 Coverage: Scope']['multi_select']
            if not len(scopes):
                return

            for item in scopes:
                tag, created = CoverageScope.objects.get_or_create(name=item['name'])
                tags.append(tag)

        except Exception as e:
            console.warn("Failed to add scope tags")
            console.warn(e)
            raise
        else:
            # console.info(f"Scope tags: {tags}")
            return tags
