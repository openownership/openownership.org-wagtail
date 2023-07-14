"""
    modules.core.forms
    ~~~~~~~~~~~~~~~~~~
    Extendable forms
"""

# 3rd party
import django.forms as forms

# Project
from consoler import console  # NOQA


class HoneyPotForm(forms.Form):
    x_phone = forms.CharField(  # This is a honey pot to catch spammers
        label="Please fill this in",
        # widget=forms.HiddenInput(),
        required=False
    )

    def clean_x_phone(self):
        """Check that nothing's been entered into the honeypot."""
        value = self.cleaned_data["x_phone"]
        if value:
            console.error('FILLED IN HONEYPOT')
            raise forms.ValidationError(self.fields["x_phone"].label)
        return value
