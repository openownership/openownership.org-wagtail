from django import forms


class CookiesForm(forms.Form):

    COOKIE_CHOICES = [('allow', 'On'), ('deny', 'Off')]

    COOKIE_TYPES = ['analytics', 'third_party']

    def __init__(self, *args, **kwargs):

        cookies = kwargs.pop('cookies', {})
        super().__init__(*args, **kwargs)

        default = cookies.get('cookieconsent_status', 'allow')

        for cookie in self.COOKIE_TYPES:

            field_key = f'{cookie}_cookies'
            cookie_key = f'{field_key}'

            self.fields[field_key] = forms.ChoiceField(
                choices=self.COOKIE_CHOICES,
                required=True,
                widget=forms.RadioSelect,
                initial=cookies.get(cookie_key, default)
            )
