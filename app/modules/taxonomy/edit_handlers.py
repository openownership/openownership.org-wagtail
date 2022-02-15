from wagtail.admin.edit_handlers import FieldPanel


class PublicationTypeFieldPanel(FieldPanel):
    """
    Provides a way to restrict which PublicationTypes are available
    in the field.

    If using this in a Page model in place of a regular FieldPanel,
    with a field like:

        publication_type = models.ForeignKey('taxonomy.PublicationType', ...)

    then the Page model should also include a method like this:

        def get_publication_type_choices(cls):
            return PublicationType.objects.filter(name='foo')

    From https://www.mashandgravy.co.uk/blog/querysets-wagtail-field-panels/
    """

    def on_form_bound(self):
        try:
            choices = self.model.get_publication_type_choices(self.model)
        except AttributeError:
            raise NotImplementedError(
                f"{self.model.__name__} uses the PublicationTypeFieldPanel() "
                "but does not have a get_publication_type_choices() method, "
                "which is required when using this panel."
            )
        self.form.fields['publication_type'].queryset = choices
        self.form.fields['publication_type'].empty_label = None
        super().on_form_bound()
