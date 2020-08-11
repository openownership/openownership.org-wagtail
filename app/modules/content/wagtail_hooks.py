from wagtail.contrib.modeladmin.options import (
    ModelAdmin, modeladmin_register
)
from .models import FAQList


class FAQListAdmin(ModelAdmin):
    model = FAQList
    menu_label = 'FAQs'
    menu_icon = 'fa-question'
    menu_order = 500
    list_display = ('name', )
    search_fields = ('name', )


modeladmin_register(FAQListAdmin)
