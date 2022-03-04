from cacheops import invalidate_all
from django.conf import settings
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _

from .mixins import Footer, NavBar

from wagtail.admin.edit_handlers import ObjectList, TabbedInterface
from wagtail.contrib.settings.models import register_setting
from wagtailcache.cache import clear_cache


@register_setting(icon="fa-bars")
class NavigationSettings(NavBar, Footer):

    class Meta:
        verbose_name = _('Navigation settings')

    def build_nav_items(self, block, menu):
        menu.append({
            'type': 'nav_item',
            'value': (block.value.href, block.value.label),
            'page': block.value.get('link_page', None),
        })
        return menu

    def build_nav(self):
        menus = {}
        for nav_menu in self.get_nav_fields():
            menu = menus[nav_menu] = []
            for block in getattr(self, nav_menu):
                if block.block_type == 'mega_menu':
                    self.build_mega_menu(block, menu)
                elif block.block_type == 'nav_item':
                    self.build_nav_items(block, menu)
        for nav_menu in self.get_footer_nav_fields():
            menu = menus[nav_menu] = []
            for block in getattr(self, nav_menu):
                if block.block_type == 'nav_item':
                    self.build_nav_items(block, menu)
        return menus

    @classmethod
    def get_nav_context(cls, site):
        obj = cls.for_site(site)
        cache_key = cls.get_cache_key_nav(site.pk)
        cached = cache.get(cache_key)

        if not cached:
            obj = cls.for_site(site)
            data = obj.build_nav()
            cache.set(cache_key, data, settings.MONTH_IN_SECONDS)  # month
            return data

        return cached

    @classmethod
    def get_cache_key_nav(cls, site_id):
        return f'{site_id}_site_nav_settings'

    def save(self, *args, **kwargs):
        cache.delete(self.get_cache_key_nav(self.site_id))
        clear_cache()
        invalidate_all()
        return super().save(*args, **kwargs)

    base_tabs = [
        ObjectList(NavBar.navigation_panels, heading=_('Navbar')),
        ObjectList(Footer.navigation_panels, heading=_('Footer')),
    ]

    edit_handler = TabbedInterface(base_tabs)
