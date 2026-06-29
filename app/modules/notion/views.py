# stdlib
import csv
from pathlib import Path

# 3rd party
import arrow
from consoler import console  # NOQA
from django.conf import settings
from django.http import FileResponse, Http404, HttpResponse
from django.utils.functional import cached_property
from django.views import View

# Project
from modules.notion.models import Commitment, CountryTag, DisclosureRegime

BASE_HEADERS = [
    "Name of register",  # Register name from Implementation tracker
    "Link",
    "Scope",
    "Register launched",
    "Data structured in BODS",
    "Responsible agency",
    "Agency type",
    "Who can access",
]

COUNTRY_HEADERS = ["", "Stage"] + BASE_HEADERS + ["ISO2", "Region"]

ALL_HEADERS = ["Country", "Stage"] + BASE_HEADERS + ["ISO2", "Region"]


class DataExportBase(View):
    """Shared functionality between the exporters for both the CountryExport and CountriesExport
    classes.
    """

    def _yes_no(self, val):
        if val is True:
            return "Yes"
        return ""

    def _format_date(self, val):
        try:
            dt = arrow.get(val)
            return dt.format("YYYY-MM-DD")
        except Exception:
            return ""

    def _get_commitment_row(self, commitment: Commitment, skip_one: bool = False) -> list:
        """Creates a data row (list) from a Commitment object

        Args:
            commitment (Commitment): The commitment objects we want the data from

        Returns:
            list: A row of data
        """
        row = []
        row.append("Commitment")
        if not skip_one:
            row.append("")
        row.append(commitment.commitment_type_name)
        # Implementation / regime fields
        row.append("")
        row.append("")
        row.append("")
        row.append("")
        row.append("")
        row.append("")
        row.append("")
        row.append("")
        row.append("")
        return row

    def _get_regime_row(self, regime: DisclosureRegime, is_single: bool = True) -> list:
        """Creates a data row (list) from a DisclosureRegime object

        Args:
            regime (DisclosureRegime): Description

        Returns:
            list: Description
        """
        row = []
        row.append("")
        if is_single:
            row.append("")
        row.append(regime.title)
        row.append(regime.public_access_register_url)
        row.append(regime.display_scope)
        row.append(regime.display_register_launched)
        row.append(self._yes_no(regime.display_data_in_bods))
        row.append(self._tag_names_to_string(regime.responsible_agency))
        row.append(regime.agency_type)
        row.append(self._tag_names_to_string(regime.who_can_access))
        return row

    def _tag_names_to_string(self, field):
        if isinstance(field, str):
            return field
        return " | ".join([tag.name for tag in field.all()])

    def _is_subnational(self, regime: DisclosureRegime) -> bool:
        return "Subnational" in [scope.name for scope in regime.coverage_scope.all()]

    def _exportable_regimes(self, country: CountryTag) -> list:
        """Regimes to list in exports: every implementation stage, excluding
        Subnational-scoped registers (which are not shown elsewhere on the site).
        """
        return [r for r in country.regimes.all() if not self._is_subnational(r)]

    def _region_name(self, country: CountryTag) -> str:
        region = country.regions.first()
        return region.name if region else ""


class CountryExport(DataExportBase):
    """A class for exporting a country's data as CSV"""

    def setup(self, request, *args, **kwargs):
        self.slug = kwargs.pop("slug")
        try:
            self.country = CountryTag.objects.get(slug=self.slug)
        except CountryTag.DoesNotExist as err:
            raise Http404 from err

        super().setup(request, *args, **kwargs)

    def get(self, *args, **kwargs):  # noqa: ARG002
        response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{self.slug}.csv"'},
        )
        self._generate_csv(response)
        return response

    def _generate_csv(self, response: HttpResponse):
        writer = csv.writer(response)
        writer.writerow(COUNTRY_HEADERS)
        row = ["" for _ in COUNTRY_HEADERS]
        row[0] = self.country.name
        row[1] = self.country.category_display
        row[10] = self.country.iso2
        row[11] = self._region_name(self.country)
        writer.writerow(row)
        for regime in self._exportable_regimes(self.country):
            writer.writerow(self._get_regime_row(regime))
        return writer


class CountriesExport(DataExportBase):
    """A class for exporting all countries' data as CSV"""

    def get(self, *args, **kwargs):  # noqa: ARG002
        response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="oo_all_country_data.csv"'},
        )
        self._generate_csv(response)
        return response

    def _generate_csv(self, response: HttpResponse):
        writer = csv.writer(response)
        writer.writerow(ALL_HEADERS)
        for country in self._all_countries:
            regimes = self._exportable_regimes(country)
            if not regimes:
                # Planning or implementation-stage countries with no register
                # still appear, so the export covers every status.
                writer.writerow(self._country_only_row(country))
                continue
            for regime in regimes:
                row = [country.name] + self._get_regime_row(regime, is_single=False) + ["", ""]
                row[1] = country.category_display
                row[10] = country.iso2
                row[11] = self._region_name(country)
                writer.writerow(row)
        return writer

    def _country_only_row(self, country: CountryTag) -> list:
        row = ["" for _ in ALL_HEADERS]
        row[0] = country.name
        row[1] = country.category_display
        row[10] = country.iso2
        row[11] = self._region_name(country)
        return row

    @cached_property
    def _all_countries(self):
        return CountryTag.objects.exclude(deleted=True).exclude(archived=True).order_by("name")


def serve_csv_file(request):  # noqa: ARG001
    file_path = Path(settings.STATIC_ROOT) / "files" / "metadata.csv"
    if file_path.exists():
        response = FileResponse(open(file_path, "rb"), content_type="text/csv")  # noqa: PTH123, SIM115
        response["Content-Disposition"] = "attachment; filename=metadata.csv"
        return response
    msg = "CSV file does not exist"
    raise Http404(msg)
