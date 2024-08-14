# stdlib

# 3rd party
from cacheops import cached
from consoler import console

# Project
from modules.bots.notionbot import notionbot
from modules.notion.models import CountryTag


HEADERS_COUNTRY_TRACKER = ["OO Support", "ISO2"]


HEADERS_COMMITMENT_TRACKER = [
    "Country",
    "Date",
    "Link",
    "Commitment type",
    "Central register",
    "Public register",
    "Summary Text",
    "All sectors",
]


# HEADERS_DISCLOSURE_REGIMES = [
#     "Country",
#     "1.1 Definition: Legislation URL",
#     "2.3 Coverage: Legislation URL",
#     "4.1 Central register",
#     "5.1 Public access",
#     "5.1.1 Public access: Register URL",
#     "4.2 Year launched",
#     "6.1 Structured data",
#     "6.3 API available",
#     "6.4 Data published in BODS",
#     "6.5 Data on OO Register",
#     "8.4 Legislation URL",
#     "1.2 Threshold",
#     "3.1 Sufficient detail: Legislation URL",
#     "5.4.1 Protection regime URL",
#     "5.5 Legal basis for publication URL",
#     "9 Sanctions and enforcement: Legislation URL",
#     "2.1 Coverage: Scope",
#     "0 Stage",
# ]


HEADERS_DISCLOSURE_REGIMES: list = [
    'Last edited',
    'Implementation stage',  # 0 Stage
    'Register URL',  # 5.1 Public access: Register URL
    'Scope',  # 2.1 Coverage: Scope
    'Threshold (%)',  # 1.2 Definition: Threshold
    'Year launched',  # 5.1.1 Year launched
    'Who can access',

    # 'Access features',
    # 'Access regime details',
    'Agency type',
    # 'Country',
    # 'Coverage',
    # 'Definition',
    # 'Details collected',
    # 'Forms',
    # 'Last updated by',
    # 'Licence and data use policy details',
    # 'OO Principle focus',
    # 'Policy aims details',
    # 'Privacy and data protection details',
    # 'Protection regime',
    # 'Register cost and business model',
    # 'Register name',
    'Responsible agency',
    # 'Sanctions and enforcement details',
    # 'Stated policy aims',
    # 'Structured data details',
    # 'Trips',
    # 'Up-to-date and historical data details',
    # 'User guidance',
    # 'Vendor/supplier',
    # 'Verification details',

]

HEADERS_DISCLOSURE_REGIMES_SUB: list = [
    'API available',  # 6.2 API available
    'Bulk data available',  # 6.1 Bulk data available
    'Data on OO Register',  # 6.4 Data on OO Register
    'Data published in BODS',  # 6.3 Data published in BODS
    'Structured data',  # 6 Structured data

    # 'API documentation',
    # 'API URL',
    # 'Bulk data URL',
    # 'Country',
    # 'Data analysed/mapped',
    # 'Data analysis/mapping',
    # 'Disclosure regime',
    # 'Exact ownership values',
    # 'Identifiers information',
    # 'Identifiers used',
    # 'Licence URL',
    # 'Notes and remarks',
    # 'Open licence',
    # 'Sufficient information for full ownership chains',
    # 'Title',
    # 'User group',
]


def check_headers(tracker: str, data: dict) -> bool:
    if tracker == "Country":
        return _check_headers(HEADERS_COUNTRY_TRACKER, data, tracker)
    if tracker == "Commitment":
        return _check_headers(HEADERS_COMMITMENT_TRACKER, data, tracker)
    if tracker == "Disclosure Regime":
        return _check_headers(HEADERS_DISCLOSURE_REGIMES, data, tracker)
    if tracker == "Disclosure Regime Sub":
        return _check_headers(HEADERS_DISCLOSURE_REGIMES_SUB, data, tracker)
    return False


def _check_headers(expected_headers: list, data: dict, tracker: str) -> bool:
    # if tracker == "Country":
    #     import ipdb; ipdb.set_trace()
    missing = []
    for item in expected_headers:
        try:
            data["results"][0]["properties"][item]
        except KeyError as e:  # noqa: PERF203
            console.warn(e)
            missing.append(item)

    if len(missing):
        subject = f"Found {len(missing)} missing headers in {tracker} tracker..."
        body = ", ".join(missing)
        notionbot.fail(subject, body)
        return False

    return True


@cached(timeout=60 * 60)
def countries_json():
    try:
        countries = CountryTag.objects.all()
        data = []
        for item in countries:
            data.append({"name": item.name, "iso2": item.iso2, "url": item.url})  # noqa: PERF401
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
            data.append(  # noqa: PERF401
                {
                    "name": item.name,
                    "iso2": item.iso2,
                    "url": item.url,
                    "lat": item.lat,
                    "lon": item.lon,
                    "oo_support": item.oo_support,
                    # 'committed_central': item.committed_central,
                    # 'committed_public': item.committed_public,
                    # 'implementation_central': item.implementation_central,
                    # 'implementation_public': item.implementation_public,
                    "category": item.category,
                },
            )
        rv = data
    except Exception as e:
        console.warn(e)
    else:
        return rv
