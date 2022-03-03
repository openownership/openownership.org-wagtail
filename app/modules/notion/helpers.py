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


@cached(timeout=60 * 60)
def map_json():
    try:
        countries = CountryTag.objects.all()
        data = []
        for item in countries:
            data.append({
                'name': item.name,
                'url': item.url,
                'lat': item.lat,
                'lon': item.lon,
                'committed_central': item.committed_central,
                'committed_public': item.committed_public,
                'implementation_central': item.implementation_central,
                'implementation_public': item.implementation_public,
            })
        rv = json.dumps(data)
    except Exception as e:
        console.warn(e)
    else:
        return rv
