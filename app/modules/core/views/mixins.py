class AppPageContextMixin(object):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if hasattr(self, 'parent_page'):
            try:
                context.update(self.parent_page.get_context(self.request, **kwargs))
            except Exception:
                pass

        return context
