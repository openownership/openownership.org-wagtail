NAV_ITEM_PAGE = {
    'type': 'nav_item',
    'value': {
        'link_type': None,
        'link_page': None,
        'link_url': None,
        'link_label': 'Link to home page'
    }
}

NAV_ITEM_URL = {
    'type': 'nav_item',
    'value': {
        'link_type': None,
        'link_page': None,
        'link_url': 'http://www.livechat.com',
        'link_label': 'Find a centre'
    }
}

MEGA_MENU = {
    'type': 'mega_menu',
    'value': {
        'nav_item': {
            'link_type': None,
            'link_page': None,
            'link_url': None,
            'link_label': 'Link to home page'
        },
        'objects': [
            {
                'type': 'nav_item',
                'value': {
                    'link_type': None,
                    'link_page': None,
                    'link_url': 'http://example.org',
                    'link_label': 'Tools to help you cope'
                }
            },
            {
                'type': 'sub_menu',
                'value': {
                    'nav_item': {
                        'link_type': None,
                        'link_page': None,
                        'link_url': 'http://www.findacentre.com',
                        'link_label': 'Find a centre'
                    },
                    'links': [
                        {
                            'link_type': None,
                            'link_page': None,
                            'link_url': 'http://www.livechat.com',
                            'link_label': 'Link to live chat'
                        },
                    ]
                }
            }
        ]
    }
}

SOCIAL_LINKS = {
    'type': 'social_links',
    'value': {
        'service': 'Twitter',
        'url': 'https://www.twitter.com'
    }
}
