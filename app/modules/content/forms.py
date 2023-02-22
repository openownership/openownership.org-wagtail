# 3rd party
from django import forms

# Project
from modules.notion.models import CountryTag
from modules.taxonomy.models import SectorTag, SectionTag, PrincipleTag, PublicationType
from modules.core.forms import HoneyPotForm


class FeedbackForm(HoneyPotForm):

    WHY_CHOICES = [
        ('inform-policymaking-legislation', 'Inform policymaking / legislation'),
        ('inform-systems-design', 'Inform systems design'),
        ('inform-advocacy', 'Inform advocacy'),
        ('academic-research', 'Academic research'),
    ]

    WHERE_CHOICES = [
        ('civil-society', 'Civil society'),
        ('government-implementer-or-contractor', 'Government (implementer or contractor)'),
        ('government-bo-data-user', 'Government (BO data user)'),
        ('private-sector', 'Private sector'),
    ]

    why_downloading = forms.ChoiceField(widget=forms.RadioSelect, choices=WHY_CHOICES)
    where_work = forms.ChoiceField(widget=forms.RadioSelect, choices=WHERE_CHOICES)


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
                widget=forms.RadioSelect(),
                initial=cookies.get(cookie_key, default)
            )


class SearchForm(forms.Form):
    q = forms.CharField(label='Search', max_length=255, required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['pt'] = forms.MultipleChoiceField(
            required=False,
            widget=forms.CheckboxSelectMultiple(),
            choices=list(PublicationType.objects.values_list("id", "name").order_by("name")),
        )

        self.fields['pr'] = forms.MultipleChoiceField(
            required=False,
            widget=forms.CheckboxSelectMultiple(),
            choices=list(PrincipleTag.objects.values_list("id", "name").order_by("name")),
        )

        self.fields['sn'] = forms.MultipleChoiceField(
            required=False,
            widget=forms.CheckboxSelectMultiple(),
            choices=list(SectionTag.objects.values_list("id", "name").order_by("name")),
        )

        self.fields['sr'] = forms.MultipleChoiceField(
            required=False,
            widget=forms.CheckboxSelectMultiple(),
            choices=list(SectorTag.objects.values_list("id", "name").order_by("name")),
        )

        self.fields['co'] = forms.MultipleChoiceField(
            required=False,
            widget=forms.CheckboxSelectMultiple(),
            choices=list(CountryTag.objects.values_list("id", "name").order_by("name")),
        )
