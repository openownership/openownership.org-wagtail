# 3rd party
from consoler import console
from django.conf import settings
from django_cron import Schedule
from django.db import IntegrityError

# Module
from modules.notion.helpers import check_headers
from modules.notion.data import COMMITMENT_TRACKER
from modules.notion.models import Commitment
from modules.notion.cron.core import NotionCronBase, NotionError


class SyncCommitments(NotionCronBase):
    RUN_EVERY_MINS = 120  # every 2 hours

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'notion.sync_commitments'

    def __init__(self, *args, **kwargs):
        self._model = Commitment
        super().__init__(*args, **kwargs)

    def do(self, data: dict = None):
        """Sync commitments from Notion

        Args:
            data (dict, optional): We're only going to pass the data in here in tests
        """

        # The ID we have for COMMITMENT_TRACKER is already the DB id
        if not data:
            data = self.fetch_all_data(COMMITMENT_TRACKER)

        if check_headers("Commitment", data):
            results = data.get('results', [])
            if len(results):
                # Do stuff here to save the data from Notion
                for item in results:
                    self._handle_commitment(item)
            else:
                # Notify of failure, probably Slack and logging
                console.warn("Commitments - Results was zero len")

            self._clean_up(data)

    def _handle_commitment(self, commitment: dict) -> bool:
        """Gets data from notion (`commitment`) and saves it as a Commitment.

        Args:
            commitment (dict): The OG Notion data, as a dict for a single commitment row

        Returns:
            bool: Success / Failure
        """
        # import ipdb; ipdb.set_trace()  # noqa: E702
        try:
            notion_id = commitment['id']
        except KeyError:
            console.warn(commitment)
            console.error("No notion ID found")

        try:
            country_id = self._get_rel_id(commitment, 'Country')
            if country_id is None:
                return False
        except Exception as error:
            console.error(error)
            if settings.DEBUG:
                import ipdb; ipdb.set_trace()  # noqa: E702

        try:
            country = None
            if country_id:
                country = self._get_country(country_id)
        except Exception as error:
            console.error(error)
            if settings.DEBUG:
                import ipdb; ipdb.set_trace()  # noqa: E702

        try:
            if country:
                obj, created = Commitment.objects.get_or_create(
                    notion_id=notion_id, country=country)
            else:
                console.warn("No related country found, skipping")
                return False
        except IntegrityError:
            # this probably already exists but with a different country
            obj = Commitment.objects.get(notion_id=notion_id)
            obj.country = country
        except Exception as error:
            console.error(error)
            if settings.DEBUG:
                import ipdb; ipdb.set_trace()  # noqa: E702
            return False

        try:
            if not self._is_updated(obj, commitment):
                return False
        except Exception as error:
            console.error(error)
            if settings.DEBUG:
                import ipdb; ipdb.set_trace()  # noqa: E702
            return False

        # This is either a new row, or it has been updated, so save stuff
        self._set_universals(obj, commitment)

        obj.oo_support = self._get_select_name(commitment, 'OO Support')
        obj.date = self._get_value(commitment, 'Date')
        obj.link = self._get_value(commitment, 'Link')
        obj.commitment_type_name = self._get_value(commitment, 'Commitment type')
        obj.central_register = self._get_value(commitment, 'Central register')
        obj.public_register = self._get_value(commitment, 'Public register')
        obj.summary_text = self._get_value(commitment, 'Summary Text')
        obj.all_sectors = self._get_value(commitment, 'All sectors')

        try:
            obj.save()
        except Exception as e:
            console.error("Failed to save")
            console.error(e)
            if settings.DEBUG:
                import ipdb; ipdb.set_trace()  # noqa: E702
        return False
