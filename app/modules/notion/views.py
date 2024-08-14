# stdlib
import csv

# 3rd party
import arrow
from consoler import console  # NOQA
from django.http import Http404, HttpResponse
from django.views import View
from django.utils.functional import cached_property

# Project
from modules.notion.models import Commitment, CountryTag, DisclosureRegime


BASE_HEADERS = [
    'Name of register',
    # Implementation / regime fields
    'Link',
    'Central register implemented',
    'Public access',
    'Scope',
    'Register launched',
    'Data structured in BODS',
    'Responsible agency',
    'Agency type',
    'Who can access',
]

COUNTRY_HEADERS = ['', 'Stage'] + BASE_HEADERS

ALL_HEADERS = ['Country', 'Stage'] + BASE_HEADERS


class DataExportBase(View):

    """Shared functionality between the exporters for both the CountryExport and CountriesExport
    classes.
    """

    def _yes_no(self, val):
        if val:
            return "Yes"
        return "No"

    def _format_date(self, val):
        try:
            dt = arrow.get(val)
            return dt.format('YYYY-MM-DD')
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

    def _get_regime_row(self, regime: DisclosureRegime) -> list:
        """Creates a data row (list) from a DisclosureRegime object

        Args:
            regime (DisclosureRegime): Description

        Returns:
            list: Description
        """
        row = []
        row.append("Implementation")
        row.append("")
        row.append("")
        row.append("")
        row.append(regime.implementation_title)
        # Implementation / regime fields
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
        return ' | '.join([tag.name for tag in field.all()])


class CountryExport(DataExportBase):

    """A class for exporting a country's data as CSV
    """

    def setup(self, request, *args, **kwargs):
        self.slug = kwargs.pop('slug')
        try:
            self.country = CountryTag.objects.get(slug=self.slug)
        except CountryTag.DoesNotExist as err:
            raise Http404 from err

        super().setup(request, *args, **kwargs)

    def get(self, *args, **kwargs):  # noqa: ARG002
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': f'attachment; filename="{self.slug}.csv"'},
        )
        self._generate_csv(response)
        return response

    def _generate_csv(self, response: HttpResponse):
        writer = csv.writer(response)
        writer.writerow(COUNTRY_HEADERS)
        row = ["", "", "", "", "", "", "", "", "", "", "", ""]
        row[0] = self.country.name
        row[1] = self.country.category_display
        writer.writerow(row)
        for commitment in self.country.commitments.all():
            writer.writerow(self._get_commitment_row(commitment))
        for regime in self.country.regimes.all():
            if regime.display:
                writer.writerow(self._get_regime_row(regime))
        return writer


class CountriesExport(DataExportBase):

    """A class for exporting all countries' data as CSV
    """

    def get(self, *args, **kwargs):  # noqa: ARG002
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="oo_all_country_data.csv"'},
        )
        self._generate_csv(response)
        return response

    def _generate_csv(self, response: HttpResponse):
        writer = csv.writer(response)
        writer.writerow(ALL_HEADERS)
        for country in self._all_countries:
            for commitment in country.commitments.all():
                row = [country.name] + self._get_commitment_row(commitment, skip_one=True)
                # Replace "Commitment" Type with stage/category:
                row[1] = country.category_display
                writer.writerow(row)
            for regime in country.regimes.all():
                if regime.display:
                    row = [country.name] + self._get_regime_row(regime)
                    # Replace "Implementation" Type with stage/category:
                    row[1] = country.category_display
                    writer.writerow(row)
        return writer


    @cached_property
    def _all_countries(self):
        countries = CountryTag.objects.exclude(
            deleted=True, archived=True).order_by('name').all()
        return countries
