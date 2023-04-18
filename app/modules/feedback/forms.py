from consoler import console
from django import forms
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

    def post(self, request, *args, **kwargs):
        form = self(request.POST)
        console.info("Form submat!")
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
