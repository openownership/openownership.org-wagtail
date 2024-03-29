from modules.notion.samples.commitments import COMMITMENTS, COMMITMENTS_WRONG
from modules.notion.samples.countries import COUNTRIES, COUNTRIES_WRONG
from modules.notion.samples.regimes import REGIMES, REGIMES_WRONG
from modules.notion.samples.regimes_sub import REGIMES_SUB, REGIMES_SUB_WRONG

from modules.notion.models import CountryTag, Commitment, DisclosureRegime, CoverageScope
from modules.notion.cron import (
    SyncRegimes, SyncCountries, SyncCommitments, NotionCronBase, SyncRegimesSub,
)
from modules.notion.helpers import check_headers

from .data import (
    LEGISLATION_RICHTEXT,
    LEGISLATION_RICHTEXT_TARGET,
    COMPLEX_RICHTEXT,
    COMPLEX_RICHTEXT_TARGET,
    MEGA_RICHTEXT,
    MEGA_RICHTEXT_TARGET,
)


def test_sync_countries():
    """There's 194 entries in the sample COUNTRIES data
    """
    s = SyncCountries()
    s.do(data=COUNTRIES)
    assert CountryTag.objects.count() == 209
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
    assert Commitment.objects.count() == 259


def test_sync_regimes():
    """There's 95 entries in the sample REGIMES data,
    but it relies on the countries data, so we have to sync that first.
    """
    _countries = SyncCountries()
    _countries.do(data=COUNTRIES)
    s = SyncRegimes()
    s.do(data=REGIMES)
    # for item in COMMITMENTS['results']:
    #     com = Commitment.objects.filter(notion_id=item['id']).first()
    #     assert com is not None
    assert DisclosureRegime.objects.count() == 101
    assert CoverageScope.objects.count() == 7
    assert DisclosureRegime.objects.filter(coverage_scope__isnull=False).first() is not None


def test_sync_regimes_sub():
    """Sub regimes require regimes to sync first.
    There's 35 items in the regimes_sub test data.
    """
    _countries = SyncCountries()
    _countries.do(data=COUNTRIES)
    _regimes = SyncRegimes()
    _regimes.do(data=REGIMES)
    assert DisclosureRegime.objects.count() == 101
    assert CoverageScope.objects.count() == 7
    assert DisclosureRegime.objects.filter(coverage_scope__isnull=False).first() is not None
    s = SyncRegimesSub()
    s.do(data=REGIMES_SUB)
    # Test that we've saved the data from the sub to the disclosure regime model
    dr = DisclosureRegime.objects.get(notion_id='de1064c1-7281-4b76-9575-bcc5b34e526d')
    assert dr.api_available == 'Yes'
    assert dr.bulk_data_available == 'Yes'
    assert dr.on_oo_register == ''
    assert dr.data_in_bods == 'No'
    assert dr.structured_data == 'Yes'



def test_legislation_rich_text():
    """The data in LEGISLATION_RICHTEXT should get transformed into...
    <a href="https://lovdata.no/dokument/LTI/forskrift/2021-06-21-2056">
        https://lovdata.no/dokument/LTI/forskrift/2021-06-21-2056
    </a>
    """
    data = LEGISLATION_RICHTEXT
    cron = NotionCronBase()
    value = cron._get_value(data, '2.3 Coverage: Legislation URL')
    assert value is not None
    assert '<a href="https://lovdata.no/dokument/LTI/forskrift/2021-06-21-2056">' in value
    assert 'forskrift/2021-06-21-2056</a>' in value
    assert value == LEGISLATION_RICHTEXT_TARGET


def test_complex_rich_text():
    """
    """
    data = COMPLEX_RICHTEXT
    cron = NotionCronBase()
    value = cron._get_value(data, 'Summary Text')
    assert value is not None
    assert value == COMPLEX_RICHTEXT_TARGET


def test_mega_rich_text():
    """
    """
    data = MEGA_RICHTEXT
    cron = NotionCronBase()
    value = cron._get_value(data, '1.1 Definition: Legislation URL')
    assert value is not None
    assert value == MEGA_RICHTEXT_TARGET


def test_check_headers_country():
    data = COUNTRIES
    res = check_headers("Country", data)
    assert res is True


def test_check_headers_commitment():
    data = COMMITMENTS
    res = check_headers("Commitment", data)
    assert res is True


def test_check_headers_regime():
    data = REGIMES
    res = check_headers("Disclosure Regime", data)
    assert res is True


def test_check_headers_country_wrong():
    data = COUNTRIES_WRONG
    res = check_headers("Country", data)
    assert res is False


def test_check_headers_commitment_wrong():
    data = COMMITMENTS_WRONG
    res = check_headers("Commitment", data)
    assert res is False


def test_check_headers_regime_wrong():
    data = REGIMES_WRONG
    res = check_headers("Disclosure Regime", data)
    assert res is False


def test_check_headers_regime_sub_wrong():
    data = REGIMES_SUB_WRONG
    res = check_headers("Disclosure Regime Sub", data)
    assert res is False
