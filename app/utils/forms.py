from itertools import groupby
from django.forms.models import ModelChoiceIterator, ModelMultipleChoiceField


class GroupedModelMultipleChoiceField(ModelMultipleChoiceField):

    def __init__(self, group_by_field, group_label=None, *args, **kwargs):
        """
        ``group_by_field`` is the name of a field on the model
        ``group_label`` is a function to return a label for each choice group

        """
        super(GroupedModelMultipleChoiceField, self).__init__(*args, **kwargs)
        self.group_by_field = group_by_field
        if group_label is None:
            self.group_label = lambda group: group
        else:
            self.group_label = group_label

    def _get_choices(self):
        if hasattr(self, '_choices'):
            return self._choices
        return GroupedModelChoiceIterator(self)
    choices = property(_get_choices, ModelMultipleChoiceField._set_choices)


class GroupedModelChoiceIterator(ModelChoiceIterator):

    def __iter__(self):
        """Now yields grouped choices."""
        if self.field.empty_label is not None:
            yield ("", self.field.empty_label)
        for group, choices in groupby(
                self.queryset.all(),
                lambda row: getattr(row, self.field.group_by_field)):
            if group is None:
                for ch in choices:
                    yield self.choice(ch)
            else:
                yield (
                    self.field.group_label(group),
                    [self.choice(ch) for ch in choices])
