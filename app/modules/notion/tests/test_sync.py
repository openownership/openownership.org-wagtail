from modules.notion.samples.commitments import COMMITMENTS
from modules.notion.samples.countries import COUNTRIES
from modules.notion.samples.regimes import REGIMES

from modules.notion.models import CountryTag, Commitment
from modules.notion.cron import (
    SyncRegimes, SyncCountries, SyncCommitments, DisclosureRegime, CoverageScope
)


def test_sync_countries():
    """There's 194 entries in the sample COUNTRIES data
    """
    s = SyncCountries()
    s.do(data=COUNTRIES)
    assert CountryTag.objects.count() == 194
    assert CountryTag.objects.filter(name='Mexico').count() == 1


def test_sync_commitments():
    """There's 188 entries (BUT ONE IS EMPTY) in the sample COMMITMENTS data,
    but it relies on the countries data, so we have to sync that first.
    """
    _countries = SyncCountries()
    _countries.do(data=COUNTRIES)
    s = SyncCommitments()
    s.do(data=COMMITMENTS)
    # for item in COMMITMENTS['results']:
    #     com = Commitment.objects.filter(notion_id=item['id']).first()
    #     assert com is not None
    assert Commitment.objects.count() == 187


def test_sync_regimes():
    """There's 59 entries in the sample REGIMES data,
    but it relies on the countries data, so we have to sync that first.
    """
    _countries = SyncCountries()
    _countries.do(data=COUNTRIES)
    s = SyncRegimes()
    s.do(data=REGIMES)
    # for item in COMMITMENTS['results']:
    #     com = Commitment.objects.filter(notion_id=item['id']).first()
    #     assert com is not None
    assert DisclosureRegime.objects.count() == 59
    assert CoverageScope.objects.count() == 6
    assert DisclosureRegime.objects.filter(coverage_scope__isnull=False).first() is not None
