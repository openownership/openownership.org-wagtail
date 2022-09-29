# 3rd party
from django import forms
from wagtail.admin.widgets import AdminDateInput
from wagtail.documents.forms import BaseDocumentForm
from wagtail.images.widgets import AdminImageChooser


class DocumentDownloadFilterForm(forms.Form):

    title = forms.CharField(required=False)

    download_start_date = forms.DateField(
        label="Downloaded since (inclusive)",
        required=False,
        widget=AdminDateInput
    )

    download_end_date = forms.DateField(
        label="Downloaded before (inclusive)",
        required=False,
        widget=AdminDateInput
    )

    upload_start_date = forms.DateField(
        label="Uploaded since (inclusive)",
        required=False,
        widget=AdminDateInput
    )

    upload_end_date = forms.DateField(
        label="Uploaded before (inclusive)",
        required=False,
        widget=AdminDateInput
    )

    exclude_authenticated = forms.BooleanField(
        label='Exclude logged-in users',
        required=False
    )

    exclude_empty = forms.BooleanField(
        label='Exclude documents with zero downloads',
        required=False
    )


# 3rd party
class SiteDocumentForm(BaseDocumentForm):

    class Meta(BaseDocumentForm.Meta):

        widgets = BaseDocumentForm.Meta.widgets
        widgets.update({
            'thumbnail': AdminImageChooser
        })
