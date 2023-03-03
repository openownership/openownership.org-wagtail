# stdlib
import csv

# 3rd party
import arrow
from consoler import console  # NOQA
from django.http import Http404, HttpResponse
from django.views import View
from django.utils.functional import cached_property
from cacheops import cached

# Project
from modules.notion.models import Commitment, CountryTag, DisclosureRegime


COUNTRY_HEADERS = [
    'Type',
    'Name',
    'Central',
    'Public access',
    'All sectors',
    'Date',
    'Link',
    'Central register implemented',
    'Public access',
    'Scope',
    'Register launched',
    'Threshold used to determine beneficial ownership',
    'Structured data publicly available',
    'Available as BODS',
    'Available via API',
    'Available on the OO register'
]

ALL_HEADERS = ['Country'] + COUNTRY_HEADERS


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

    def _get_commitment_row(self, commitment: Commitment) -> list:
        """Creates a data row (list) from a Commitment object

        Args:
            commitment (Commitment): The commitment objects we want the data from

        Returns:
            list: A row of data
        """
        row = []
        row.append("Commitment")
        row.append(commitment.commitment_type_name)
        row.append(self._yes_no(commitment.central_register))
        row.append(self._yes_no(commitment.public_register))
        row.append(self._yes_no(commitment.all_sectors))
        row.append(self._format_date(commitment.date))
        row.append(commitment.link)
        # Implementation fields
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
        row.append(regime.implementation_title)
        row.append("")
        row.append("")
        row.append("")
        row.append("")
        row.append("")
        # Implementation fields
        row.append(self._yes_no(regime.implementation_central))
        row.append(self._yes_no(regime.implementation_public))
        row.append(regime.display_scope)
        row.append(regime.display_register_launched)
        row.append(regime.display_threshold)
        row.append(self._yes_no(regime.display_structured_data))
        row.append(self._yes_no(regime.display_data_in_bods))
        row.append(self._yes_no(regime.display_api))
        row.append(self._yes_no(regime.display_oo_register))
        return row


class CountryExport(DataExportBase):

    """A class for exporting a country's data as CSV
    """

    def setup(self, request, *args, **kwargs):
        self.slug = kwargs.pop('slug')
        try:
            self.country = CountryTag.objects.get(slug=self.slug)
        except CountryTag.DoesNotExist:
            raise Http404

        super().setup(request, *args, **kwargs)

    def get(self, *args, **kwargs):
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': f'attachment; filename="{self.slug}.csv"'},
        )
        self._generate_csv(response)
        return response

    def _generate_csv(self, response: HttpResponse):
        writer = csv.writer(response)
        writer.writerow(COUNTRY_HEADERS)
        for commitment in self.country.commitments.all():
            writer.writerow(self._get_commitment_row(commitment))
        for regime in self.country.regimes.all():
            if regime.display:
                writer.writerow(self._get_regime_row(regime))
        return writer


class CountriesExport(DataExportBase):

    """A class for exporting all countries' data as CSV
    """

    def get(self, *args, **kwargs):
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
                row = [country.name] + self._get_commitment_row(commitment)
                writer.writerow(row)
            for regime in country.regimes.all():
                if regime.display:
                    row = [country.name] + self._get_regime_row(regime)
                    writer.writerow(row)
        return writer


    @cached_property
    def _all_countries(self):
        countries = CountryTag.objects.exclude(
            deleted=True, archived=True).order_by('name').all()
        return countries
