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
from loguru import logger  # NOQA

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

COUNTRY_HEADERS = ["", "Stage"] + BASE_HEADERS

ALL_HEADERS = ["Country", "Stage"] + BASE_HEADERS


class DataExportBase(View):
    """Shared functionality between the exporters for both the CountryExport and CountriesExport
    classes.
    """

    def _yes_no(self, val):
        if val.lower() == "yes":
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
        logger.info(regime.title)
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
        row = ["", "", "", "", "", "", "", "", "", ""]
        row[0] = self.country.name
        row[1] = self.country.category_display
        writer.writerow(row)
        # NO MORE COMMITMENT ROWS!
        # for commitment in self.country.commitments.all():
        #     writer.writerow(self._get_commitment_row(commitment))
        for regime in self.country.regimes.all():
            if regime.display:
                row = self._get_regime_row(regime)
                logger.info(row)
                writer.writerow(row)
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
            # NO MORE COMMITMENT ROWS!
            # for commitment in country.commitments.all():
            #     row = [country.name] + self._get_commitment_row(commitment, skip_one=True)
            #     # Replace "Commitment" Type with stage/category:
            #     row[1] = country.category_display
            #     writer.writerow(row)
            for regime in country.regimes.all():
                if regime.display:
                    row = [country.name] + self._get_regime_row(regime, is_single=False)
                    row[1] = country.category_display
                    writer.writerow(row)
        return writer

    @cached_property
    def _all_countries(self):
        countries = CountryTag.objects.exclude(deleted=True, archived=True).order_by("name").all()
        return countries


def serve_csv_file(request):  # noqa: ARG001
    file_path = Path(settings.STATIC_ROOT) / "files" / "metadata.csv"
    if file_path.exists():
        response = FileResponse(open(file_path, "rb"), content_type="text/csv")  # noqa: PTH123, SIM115
        response["Content-Disposition"] = "attachment; filename=metadata.csv"
        return response
    msg = "CSV file does not exist"
    raise Http404(msg)
