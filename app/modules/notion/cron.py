from django_cron import CronJobBase, Schedule
from modules.notion.data import COUNTRY_TRACKER, COMMITMENT_TRACKER, DISCLOSURE_REGIMES
from modules.notion.auth import get_notion_client
from modules.notion.utils import find_db_id


class NotionCronBase(CronJobBase):

    def __init__(self, *args, **kwargs):
        self.client = get_notion_client()


class SyncCountries(NotionCronBase):
    RUN_EVERY_MINS = 120  # every 2 hours

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'notion.sync_countries'

    def do(self):
        # Find the countries DB
        db_id = find_db_id(self.client, COUNTRY_TRACKER, 'Country Tracker')
        data = self.client.databases.query(database_id=db_id)
        # import ipdb; ipdb.set_trace()
        # Do stuff here to save the data from Notion


class SyncCommitments(NotionCronBase):
    RUN_EVERY_MINS = 120  # every 2 hours

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'notion.sync_commitments'

    def do(self):
        # The ID we have for COMMITMENT_TRACKER is already the DB id
        data = self.client.databases.query(database_id=COMMITMENT_TRACKER)
        # import ipdb; ipdb.set_trace()
        # Do stuff here to save the data from Notion


class SyncRegimes(NotionCronBase):
    RUN_EVERY_MINS = 120  # every 2 hours

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'notion.sync_regimes'

    def do(self):
        # The ID we have for DISCLOSURE_REGIMES is already the DB id
        data = self.client.databases.query(database_id=DISCLOSURE_REGIMES)
        # import ipdb; ipdb.set_trace()
        # Do stuff here to save the data from Notion
