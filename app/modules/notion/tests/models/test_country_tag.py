import pytest

from modules.notion.models import Commitment, CountryTag, CoverageScope, DisclosureRegime


pytestmark = pytest.mark.django_db


def test_category_liveregister():
    "Any 'publish' implementations mean it should have category of 'liveregister'"
    country = CountryTag.objects.create(notion_id="abc")
    CoverageScope.objects.create(name='Subnational')
    DisclosureRegime.objects.create(country=country, stage="Publish")
    assert country.category == "liveregister"


def test_category_implementing_disclosure_regime_not_publish():
    "If no DisclosureRegime has stage='Publish', category should be 'implementing'"
    country = CountryTag.objects.create(notion_id="abc")
    CoverageScope.objects.create(name='Subnational')
    DisclosureRegime.objects.create(country=country, stage="Foo")
    assert country.category == "implementing"


def test_category_implementing_subnational_in_coverage_scope():
    "If DisclosureRegime has subnational coverage scope, category should be 'implementing'"
    country = CountryTag.objects.create(notion_id="abc")
    subnational = CoverageScope.objects.create(name='Subnational')
    regime = DisclosureRegime.objects.create(country=country, stage="Foo")
    regime.coverage_scope.add(subnational)
    assert country.category == "implementing"


def test_category_planned():
    "If no DisclosureRegimes, but has commitments, category chould be 'planned'"
    country = CountryTag.objects.create(notion_id="abc")
    Commitment.objects.create(country=country)
    CoverageScope.objects.create(name='Subnational')
    assert country.category == "planned"


def test_category_none():
    "If no DisclosureRegimes, and no commitments, category should be None"
    country = CountryTag.objects.create(notion_id="abc")
    CoverageScope.objects.create(name='Subnational')
    assert country.category is None
