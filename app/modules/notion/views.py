import csv
from consoler import console  # NOQA
from django.http import HttpResponse
from django.views import View
from django.http import Http404

from modules.notion.models import CountryTag


HEADERS = [
    'Type',
    'Name',
    'Central',
    'Public access',
    'All sectors',
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


class CountryExport(View):

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

    def _generate_csv(self, response):
        writer = csv.writer(response)
        writer.writerow(HEADERS)
        for commitment in self.country.commitments.all():
            writer.writerow(self._get_commitment_row(commitment))
        for regime in self.country.regimes.all():
            if regime.display:
                writer.writerow(self._get_regime_row(regime))
        return writer

    def _get_commitment_row(self, commitment):
        row = []
        row.append("Commitment")
        row.append(commitment.commitment_type_name)
        row.append(self._yes_no(commitment.central_register))
        row.append(self._yes_no(commitment.public_register))
        row.append(self._yes_no(commitment.all_sectors))
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

    def _get_regime_row(self, regime):
        row = []
        row.append("Implementation")
        row.append(regime.implementation_title)
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


    def _yes_no(self, val):
        if val:
            return "Yes"
        return "No"


