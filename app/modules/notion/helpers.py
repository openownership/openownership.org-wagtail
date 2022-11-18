# stdlib
import json

# 3rd party
from cacheops import cached
from consoler import console

# Project
from modules.notion.models import CountryTag


@cached(timeout=60 * 60)
def countries_json():
    try:
        countries = CountryTag.objects.all()
        data = []
        for item in countries:
            data.append({
                'name': item.name,
                'iso2': item.iso2,
                'url': item.url
            })
        rv = json.dumps(data)
    except Exception as e:
        console.warn(e)
    else:
        return rv


def map_json():
    try:
        countries = CountryTag.objects.all()
        data = []
        for item in countries:
            data.append({
                'name': item.name,
                'iso2': item.iso2,
                'url': item.url,
                'lat': item.lat,
                'lon': item.lon,
                'oo_support': item.oo_support,
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
