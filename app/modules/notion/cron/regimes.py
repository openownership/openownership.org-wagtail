# 3rd party
from consoler import console
from django.conf import settings
from django_cron import Schedule

# Module
from modules.notion.helpers import check_headers
from modules.notion.data import DISCLOSURE_REGIMES, DISCLOSURE_REGIMES_SUB
from modules.notion.models import CoverageScope, DisclosureRegime
from modules.notion.cron.core import NotionCronBase, NotionError


class SyncRegimesSub(NotionCronBase):
    RUN_EVERY_MINS = 120  # every 2 hours

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'notion.sync_regimes_sub'

    def __init__(self, *args, **kwargs):
        self._model = DisclosureRegime
        self._triggered = False  # helpful in testing
        super().__init__(*args, **kwargs)

    def do(self, data: dict = None, force: bool = False):
        """Sync regimes sub from Notion

        Args:
            data (dict, optional): We're only going to pass the data in here in tests
        """

        # The ID we have for DISCLOSURE_REGIMES_SUB is already the DB id
        if not data:
            data = self.fetch_all_data(DISCLOSURE_REGIMES_SUB)

        if check_headers("Disclosure Regime Sub", data):
            results = data.get('results', [])
            if len(results):
                # Do stuff here to save the data from Notion
                for item in results:
                    self._handle_regime(item, force)
            else:
                # Notify of failure, probably Slack and logging
                console.warn("Regimes - Results was zero len")


    def _handle_regime(self, regime: dict, force: bool = False) -> bool:
        """Gets data from notion (`regime`) and saves it as a DisclosureRegime.

        Args:
            regime (dict): The OG Notion data, as a dict for a single regime row

        Returns:
            bool: Success / Failure
        """
        # if not self._triggered:
        #     self._triggered = True
        #     import ipdb; ipdb.set_trace()  # noqa: E702
        try:
            regime_notion_id = regime['properties']['Disclosure regime']['relation'][0]['id']
            obj = DisclosureRegime.objects.get(notion_id=regime_notion_id)
        except KeyError:
            console.warn(regime)
            console.error("No notion regime_notion_id found")
        except DisclosureRegime.DoesNotExist:
            console.warn(regime)
            console.error(f"No DisclosureRegime object found for {regime_notion_id}")
            return False

        obj.api_available = self._get_value(regime, 'API available')  # str
        obj.bulk_data_available = self._get_value(regime, 'Bulk data available')  # str
        obj.on_oo_register = self._get_value(regime, 'Data on OO Register')  # str
        obj.data_in_bods = self._get_value(regime, 'Data published in BODS')  # str
        obj.structured_data = self._get_value(regime, 'Structured data')  # str
        # console.info('-' * 80)
        # console.info('api_available', obj.api_available)
        # console.info('bulk_data_available', obj.bulk_data_available)
        # console.info('on_oo_register', obj.on_oo_register)
        # console.info('data_in_bods', obj.data_in_bods)
        # console.info('structured_data', obj.structured_data)
        obj.save()
        return True


class SyncRegimes(NotionCronBase):
    RUN_EVERY_MINS = 120  # every 2 hours

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'notion.sync_regimes'

    def __init__(self, *args, **kwargs):
        self._model = DisclosureRegime
        super().__init__(*args, **kwargs)

    def do(self, data: dict = None, force: bool = False):
        """Sync regimes from Notion

        Args:
            data (dict, optional): We're only going to pass the data in here in tests
        """

        # The ID we have for DISCLOSURE_REGIMES is already the DB id
        if not data:
            data = self.fetch_all_data(DISCLOSURE_REGIMES)

        if check_headers("Disclosure Regime", data):
            results = data.get('results', [])
            if len(results):
                # Do stuff here to save the data from Notion
                for item in results:
                    self._handle_regime(item, force)
            else:
                # Notify of failure, probably Slack and logging
                console.warn("Regimes - Results was zero len")

            self._clean_up(data)

    def _handle_regime(self, regime: dict, force: bool = False) -> bool:
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
                country=country,
            )
        else:
            console.warn("No related country found, skipping")
            return False

        if not self._is_updated(obj, regime) and not force:
            return False

        # This is either a new row, or it has been updated, so save stuff
        self._set_universals(obj, regime)
        obj.title = self._get_register_name(regime)
        scope_tags = self._get_scope_tags(regime)
        if scope_tags:
            for item in scope_tags:
                obj.coverage_scope.add(item)
                obj.coverage_scope.commit()

        obj.stage = self._get_stages(regime) or ''  # Implementation stage - multi-select
        obj.public_access_register_url = self._get_value(regime, 'Register URL') or ''
        obj.year_launched = self._get_value(regime, 'Year launched')
        obj.threshold = str(self._get_value(regime, 'Threshold (%)'))

        # REMOVED
        # obj.definition_legislation_url = self._get_value(
        #     regime, '1.1 Definition: Legislation URL',
        # )
        # obj.coverage_legislation_url = self._get_value(
        #     regime, '2.3 Coverage: Legislation URL',
        # )
        # obj.central_register = self._get_value(regime, '4.1 Central register')
        # obj.public_access = self._get_value(regime, '5.1 Public access')
        # obj.legislation_url = self._get_value(regime, '8.4 Legislation URL')
        # obj.sufficient_detail_legislation_url = self._get_value(
        #     regime, "3.1 Sufficient detail: Legislation URL",
        # )
        # obj.public_access_protection_regime_url = self._get_value(
        #     regime, "5.4.1 Protection regime URL",
        # )
        # obj.public_access_legal_basis_url = self._get_value(
        #     regime, "5.5 Legal basis for publication URL",
        # )
        # obj.sanctions_enforcement_legislation_url = self._get_value(
        #     regime, "9 Sanctions and enforcement: Legislation URL",
        # )

        try:
            obj.save()
        except Exception as e:
            console.error("Failed to save")
            console.error(e)
            if settings.DEBUG:
                import ipdb
                ipdb.set_trace()

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
            scopes = data['properties']['Scope']['multi_select']
            if not len(scopes):
                return None

            for item in scopes:
                tag, created = CoverageScope.objects.get_or_create(name=item['name'])
                tags.append(tag)

        except Exception as err:
            console.warn("Failed to add scope tags")
            console.warn(err)
            f"Failed to add scope tags - {err}"
            raise NotionError() from err
        else:
            # console.info(f"Scope tags: {tags}")
            return tags

    def _get_stages(self, data: dict) -> list:
        """Takes this dict, returns a comma separated list of values

        '0 Stage': {
            'id': '86%605',
            'type': 'multi_select',
            'multi_select': [
                {
                    'id': '486a37df-ec33-4f48-a513-c734ec2d7d8c',
                    'name': 'Systems',
                    'color': 'yellow'
                }
            ]
        },

        Args:
            data (dict): The disclosure regime row

        Returns:
            list: List of tags
        """
        try:
            stages = data['properties']['Implementation stage']['multi_select']
            if not len(stages):
                return None

            return ', '.join([item['name'] for item in stages])

        except Exception as err:
            console.warn("Failed to get Stages")
            console.warn(err)
            f"Failed to get Stages - {err}"
            raise NotionError() from err
