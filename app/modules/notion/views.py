import csv
from consoler import console  # NOQA
from django.http import HttpResponse
from django.views import View
from django.http import Http404

from modules.notion.models import CountryTag


HEADERS = [

]


class CountryExport(View):

    """A class for exporting a country's data as CSV
    """

    def setup(self, request, *args, **kwargs):
        slug = kwargs.pop('slug')
        try:
            self.country = CountryTag.objects.get(slug=slug)
        except CountryTag.DoesNotExist:
            raise Http404

        super().setup(request, *args, **kwargs)

    def get(self, *args, **kwargs):
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="somefilename.csv"'},
        )
        self._generate_csv(response)
        return response


    def _generate_csv(self, response):
        writer = csv.writer(response)
        writer.writerow(HEADERS)
        writer.writerow()
        return writer



