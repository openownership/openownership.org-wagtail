# stdlib
import csv
import io

# 3rd party
from django.http import HttpResponse
from django.template.defaultfilters import slugify

# Module
from modules.notion.models import Commitment, CountryTag, CoverageScope, DisclosureRegime
from modules.notion.views import CountriesExport, CountryExport


####################################################################################################
# Helpers
####################################################################################################


def make_country(name, iso2="XX", deleted=False):
    return CountryTag.objects.create(
        notion_id=f"nid-{slugify(name)}",
        name=name,
        slug=slugify(name),
        iso2=iso2,
        deleted=deleted,
    )


def make_regime(country, stage, scopes=(), title="Register"):
    regime = DisclosureRegime.objects.create(
        notion_id=f"r-{slugify(country.name)}-{slugify(stage)}",
        country=country,
        stage=stage,
        title=title,
    )
    for name in scopes:
        regime.coverage_scope.add(CoverageScope.objects.get_or_create(name=name)[0])
    regime.coverage_scope.commit()
    return regime


def csv_rows(view):
    response = HttpResponse(content_type="text/csv")
    view._generate_csv(response)
    return list(csv.reader(io.StringIO(response.content.decode())))


def names_in(rows):
    return {row[0] for row in rows[1:]}


####################################################################################################
# All-countries export
####################################################################################################


def test_all_country_csv_includes_every_status():
    """Planning and implementation-stage countries must appear, not only live registers."""
    CoverageScope.objects.get_or_create(name="Subnational")

    live = make_country("Liveland")
    make_regime(live, "Publish", scopes=["Full-economy"], title="Live Register")

    implementing = make_country("Implementia")
    make_regime(implementing, "Systems", scopes=["Full-economy"], title="WIP Register")

    planned = make_country("Plannedia")
    Commitment.objects.create(notion_id="c-plannedia", country=planned)

    names = names_in(csv_rows(CountriesExport()))
    assert {"Liveland", "Implementia", "Plannedia"} <= names


def test_all_country_csv_emits_row_for_country_without_registers():
    CoverageScope.objects.get_or_create(name="Subnational")
    planned = make_country("Plannedia")
    Commitment.objects.create(notion_id="c-plannedia", country=planned)

    rows = csv_rows(CountriesExport())
    planned_rows = [r for r in rows[1:] if r[0] == "Plannedia"]
    assert len(planned_rows) == 1
    assert planned_rows[0][2] == ""  # no register name


def test_all_country_csv_excludes_subnational_registers():
    CoverageScope.objects.get_or_create(name="Subnational")
    country = make_country("Subland")
    make_regime(country, "Publish", scopes=["Subnational"], title="Sub Register")

    rows = csv_rows(CountriesExport())
    subland_rows = [r for r in rows[1:] if r[0] == "Subland"]
    assert len(subland_rows) == 1  # country present, but as a country-only row
    assert subland_rows[0][2] == ""  # the Subnational register is not listed


def test_all_country_csv_excludes_soft_deleted_countries():
    CoverageScope.objects.get_or_create(name="Subnational")
    make_country("Ghostland", deleted=True)

    assert "Ghostland" not in names_in(csv_rows(CountriesExport()))


def test_all_country_csv_lists_live_register_details():
    CoverageScope.objects.get_or_create(name="Subnational")
    live = make_country("Liveland", iso2="LL")
    make_regime(live, "Publish", scopes=["Full-economy"], title="Live Register")

    rows = csv_rows(CountriesExport())
    live_rows = [r for r in rows[1:] if r[0] == "Liveland"]
    assert len(live_rows) == 1
    assert live_rows[0][2] == "Live Register"
    assert live_rows[0][10] == "LL"


####################################################################################################
# Single-country export
####################################################################################################


def test_single_country_csv_includes_non_live_regimes():
    CoverageScope.objects.get_or_create(name="Subnational")
    implementing = make_country("Implementia")
    make_regime(implementing, "Systems", scopes=["Full-economy"], title="WIP Register")

    view = CountryExport()
    view.country = implementing
    view.slug = implementing.slug

    titles = [row[2] for row in csv_rows(view)]
    assert "WIP Register" in titles
