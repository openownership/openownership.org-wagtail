import json
from consoler import console
from cacheops import cached

from modules.notion.models import CountryTag


@cached(timeout=60 * 60)
def countries_json():
    try:
        countries = CountryTag.objects.all()
        data = []
        for item in countries:
            data.append({
                'name': item.name,
                'url': item.url
            })
        rv = json.dumps(data)
    except Exception as e:
        console.warn(e)
    else:
        return rv
