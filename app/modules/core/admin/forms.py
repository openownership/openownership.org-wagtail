from django import forms
from django_select2.forms import Select2Widget


class DocumentDownloadFilterForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=None,
        widget=Select2Widget(attrs={
            'onchange': 'go_from_select("?user=" + this.options[this.selectedIndex].value)'
        }),
    )

    document = forms.ModelChoiceField(
        queryset=None,
        widget=Select2Widget(attrs={
            'onchange': 'go_from_select("?document=" + this.options[this.selectedIndex].value)'
        }),
    )

    def get_document_name(self, obj):
        try:
            if obj.title.startswith('Session '):
                return '{} ({})'.format(obj.title, obj.filename)
        except Exception:
            pass
        return obj.title

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['document'].label_from_instance = \
            lambda obj: self.get_document_name(obj)
