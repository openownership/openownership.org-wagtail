from consoler import console
from django import forms
from modules.core.forms import HoneyPotForm


WHY_CHOICES = [
    ('inform-policymaking-legislation', 'Inform policymaking / legislation'),
    ('inform-systems-design', 'Inform systems design'),
    ('inform-advocacy', 'Inform advocacy'),
    ('academic-research', 'Academic research'),
    ('other', 'Other'),
]

WHERE_CHOICES = [
    ('civil-society', 'Civil society'),
    ('government-implementer-or-contractor', 'Government (implementer or contractor)'),
    ('government-bo-data-user', 'Government (BO data user)'),
    ('private-sector', 'Private sector'),
    ('other', 'Other'),
]


class FeedbackForm(HoneyPotForm):

    why_downloading = forms.ChoiceField(widget=forms.RadioSelect, choices=WHY_CHOICES)
    where_work = forms.ChoiceField(widget=forms.RadioSelect, choices=WHERE_CHOICES)

    why_other = forms.CharField(required=False, widget=forms.Textarea)
    where_other = forms.CharField(required=False, widget=forms.Textarea)

    page_id = forms.IntegerField(required=True, widget=forms.HiddenInput())
    # submission_id = forms.UUIDField(required=True, widget=forms.HiddenInput())

