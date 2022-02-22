from modules.notion.samples.commitments import COMMITMENTS
from modules.notion.samples.countries import COUNTRIES
from modules.notion.samples.regimes import REGIMES

from modules.notion.models import CountryTag
from modules.notion.cron import SyncRegimes, SyncCountries, SyncCommitments


def test_sync_countries():
    """There's 100 entries in the sample COUNTRIES data
    """
    s = SyncCountries()
    s.do(data=COUNTRIES)
    assert CountryTag.objects.count() == 100
