# stdlib
import json

# 3rd party
from cacheops import cached
from consoler import console

# Project
from modules.bots.notionbot import notionbot
from modules.notion.models import CountryTag


HEADERS_COUNTRY_TRACKER = [
    'OO Support', 'ISO2'
]


HEADERS_COMMITMENT_TRACKER = [
    'Country', 'Date', 'Link', 'Commitment type',
    'Central register', 'Public register', 'Summary Text', 'All sectors'
]


HEADERS_DISCLOSURE_REGIMES = [
    'Country', '1.1 Definition: Legislation URL', '2.3 Coverage: Legislation URL',
    '4.1 Central register', '5.1 Public access', '5.1.1 Public access: Register URL',
    '4.2 Year launched', '6.1 Structured data', '6.3 API available', '6.4 Data published in BODS',
    '6.5 Data on OO Register', '8.4 Legislation URL', '1.2 Threshold',
    "3.1 Sufficient detail: Legislation URL", "5.4.1 Protection regime URL",
    "5.5 Legal basis for publication URL", "9 Sanctions and enforcement: Legislation URL",
    '2.1 Coverage: Scope', '0 Stage'
]


def check_headers(tracker: str, data: dict) -> bool:
    if tracker == "Country":
        return _check_headers(
            HEADERS_COUNTRY_TRACKER,
            data,
            tracker
        )
    elif tracker == "Commitment":
        return _check_headers(
            HEADERS_COMMITMENT_TRACKER,
            data,
            tracker
        )
    elif tracker == "Disclosure Regime":
        return _check_headers(
            HEADERS_DISCLOSURE_REGIMES,
            data,
            tracker
        )


def _check_headers(expected_headers: list, data: dict, tracker: str) -> bool:
    # if tracker == "Country":
    #     import ipdb; ipdb.set_trace()
    missing = []
    for item in expected_headers:
        try:
            data['results'][0]['properties'][item]
        except KeyError as e:
            console.warn(e)
            missing.append(item)

    if len(missing):
        subject = f'Found {len(missing)} missing headers in {tracker} tracker...'
        body = ', '.join(missing)
        notionbot.fail(subject, body)
        return False

    return True


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
        rv = data
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
        rv = data
    except Exception as e:
        console.warn(e)
    else:
        return rv
