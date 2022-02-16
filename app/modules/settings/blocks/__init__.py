from .nav_settings import NavItem, NavMegaMenu
from .site_settings import SocialMediaItem

navbar_blocks = [
    ('nav_item', NavItem()),
    ('mega_menu', NavMegaMenu()),
]

footer_nav_blocks = [
    ('nav_item', NavItem()),
]

social_media_blocks = [
    ('social_links', SocialMediaItem())
]
