# stdlib
from typing import Union, Optional
from datetime import datetime

# 3rd party
import arrow
from loguru import logger
from consoler import console
from django.conf import settings
from django_cron import CronJobBase
from django.db.models import Model

# Project
from modules.bots.notionbot import notionbot

# Module
from modules.notion.auth import get_notion_client
from modules.notion.models import CountryTag


DEFAULT_DATE = arrow.get('1970-01-01').datetime



class NotionError(Exception):
    message = ''

    def __init__(self, message=''):
        self.message = message
        notionbot.fail(message)


class NotionCronBase(CronJobBase):

    def __init__(self, *args, **kwargs):  # noqa: ARG002
        self.client = get_notion_client()

    def _clean_up(self, data: dict) -> None:
        """Looks through the `notion_id` of `self._model.objects.all()` and checks to see if
        it still exists in the `data`. If it doesn't, that row is gone from Notion and our instance
        should be deleted. However, we're doing soft-deletes for fear of breaking data integrity
        due to an accident on Notion.

        Args:
            data (dict): The data from Notion.
        """
        objects = self._model.objects.all()
        data_string = str(data)
        for item in objects:
            if item.notion_id not in data_string:
                logger.warning(f"Deleting {item}")
                item.deleted = True
                item.save()

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
            if settings.DEBUG:
                import ipdb
                ipdb.set_trace()
            else:
                raise
        except Exception as err:
            logger.error(err)
            if settings.DEBUG:
                import ipdb
                ipdb.set_trace()
            msg = f"Error fetching data - {err}"
            raise NotionError(msg) from err

        return initial_data

    def _fetch(self, db_id: str, next_cursor: str = None):
        logger.info(f"FETCH: {db_id} / {next_cursor}")
        data = self.client.databases.query(database_id=db_id, start_cursor=next_cursor)
        return data

    def _set_universals(self, obj: Model, data: dict) -> bool:
        """Sets the fields that are universal to our Notion model

        Args:
            obj (dict): The object we're currently handling.

        Returns:
            bool: Whether it succeeded or not
        """
        # logger.info(f"_set_universals: {obj} / {data}")
        try:
            obj.notion_created = self._get_created(data)
            obj.notion_updated = self._get_updated(data)
            obj.archived = data.get('archived', False)
        except Exception as e:
            logger.warning(e)
            return False
        else:
            return True

    def _get_created(self, data: dict) -> datetime:
        """Used for the notion_created datetime.
        We get this from data['created_time']

        Args:
            date_str (str): Description
        """
        # logger.info(f"_get_created: {data}")
        date_str = data.get('created_time', '1970-01-01')
        try:
            return arrow.get(date_str).datetime
        except Exception as e:
            logger.warning(e)
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
            logger.warning(e)
            return DEFAULT_DATE

    def _get_value(self, data: dict, property_name: str) -> Optional[Union[int, str]]:
        """Will try to access any Notion data type by inspecting
        data['properties'][property_name]['type'] and then handing it off to the right method.
        """
        notion_type = data['properties'][property_name]['type']
        if notion_type == 'number':
            return self._get_number(data, property_name)
        if notion_type == 'rich_text':
            return self._get_rich_text(data, property_name)
        if notion_type == 'select':
            return self._get_select_name(data, property_name)
        if notion_type == 'relation':
            return self._get_rel_id(data, property_name)
        if notion_type == 'url':
            return self._get_url(data, property_name)
        if notion_type == 'checkbox':
            return self._get_bool(data, property_name)
        if notion_type == 'date':
            return self._get_date(data, property_name)

        return ""

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
            logger.warning("Failed to get Title")
            logger.warning(e)
            return ''
        return ''

    def _get_register_name(self, data: dict) -> str:
        """
        A Notion `Register name` presents like this, we just want the plain_text...

        'properties': {
            'Register name': {
                'id': 'title',
                'type': 'title',
                'title': [
                    {
                        'type': 'text',
                        'text': {
                            'content': 'Register of Beneficial Owners of Legal Persons',
                            'link': None,
                        },
                        'annotations': {
                            'bold': False,
                            'italic': False,
                            'strikethrough': False,
                            'underline': False,
                            'code': False,
                            'color': 'default',
                        },
                        'plain_text': 'Register of Beneficial Owners of Legal Persons',
                        'href': None,
                    },
                ],
            },
        }
        """
        try:
            return data['properties']['Register name']['title'][0]['plain_text']
        except Exception as e:
            logger.warning("Failed to get Register name")
            logger.warning(e)
            return ''
        return ''

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
        if property_name not in data['properties']:
            return ''
        try:
            if data['properties'][property_name]['select'] is not None:
                if 'name' in data['properties'][property_name]['select']:
                    return data['properties'][property_name]['select']['name']
                return ''
        except Exception as e:
            logger.warning(f"Failed to get select for {property_name}")
            logger.warning(e)
            if settings.DEBUG:
                import ipdb
                ipdb.set_trace()
            return ''
        return ''

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
            logger.warning(e)
            return ''
        return ''

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
            logger.warning(e)
            return ''
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
                link = item['text']['link']
                if item['type'] == 'text' and item['text']['link'] is None:
                    result += f"{item['text']['content']}"
                elif item['type'] == 'text' and link is not None and link != {}:
                    url = item['text']['link']['url']
                    linked_text = item['text']['content']
                    href = f'<a href="{url}">{linked_text}</a>'
                    result += href
            return result
        except Exception as e:
            logger.warning(e)
            if settings.DEBUG:
                import ipdb
                ipdb.set_trace()
            return ''
        return ''

    def _get_url(self, data: dict, property_name: str) -> str:
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
            return data['properties'][property_name]['url'] or ''
        except Exception as e:
            logger.warning(e)
            # import ipdb; ipdb.set_trace()
            return ''
        return ''

    def _get_number(self, data: dict, property_name: str) -> str:
        """A number field in Notion presents like this, we just want the number key

        'properties': {
            '1.2 Threshold': {
                'id': '%24I.J',
                'type': 'number',
                'number': 23
            },
        }

        Args:
            data (dict): The dict we're grabbing the name from
        """
        try:
            return data['properties'][property_name]['number']
        except Exception as e:
            logger.warning(e)
            return ''
        return ''

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
            logger.warning(e)
            return False
        return False

    def _get_date(self, data: dict, property_name: str) -> Optional[datetime]:
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
                ds = data['properties'][property_name]['date']['start']
                dt = arrow.get(ds).datetime
                return dt
        except Exception as e:
            logger.warning(e)
            return None
        return None

    def _is_updated(self, obj: Model, data: dict) -> bool:
        try:
            _notion_updated = data.get('last_edited_time')
            last_updated = arrow.get(_notion_updated).datetime
            our_updated = obj.notion_updated
        except Exception:
            logger.error(f"Failed to get updated datetime from {_notion_updated}")
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
            logger.warning(e)
            logger.warning(notion_id)
