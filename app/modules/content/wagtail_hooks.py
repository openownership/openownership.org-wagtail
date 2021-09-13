from wagtail.contrib.modeladmin.options import (
    ModelAdmin, modeladmin_register
)
from .models import FAQList, NewsCategory


class FAQListAdmin(ModelAdmin):
    model = FAQList
    menu_label = 'FAQs'
    menu_icon = 'fa-question'
    menu_order = 500
    list_display = ('name', )
    search_fields = ('name', )


modeladmin_register(FAQListAdmin)


class NewsCategoryModelAdmin(ModelAdmin):
    add_to_settings_menu = False
    list_display = ('name', )
    search_fields = ('name', )
    prepopulated_fields = {"slug": ("name",)}
    menu_order = 400
    menu_icon = 'tag'
    menu_label = 'Categories'
    model = NewsCategory


modeladmin_register(NewsCategoryModelAdmin)
