"""
notion.tests.fakes

Stand-ins for the Meilisearch client, so the search and query layers can be
tested without a server. The test settings point Wagtail at the database search
backend and carry no Meilisearch host, so there is nothing real to talk to.

`FakeIndex.search` is deliberately dumb. It understands only the exact
`attribute IN [...]` grammar that `search.build_filter` emits, and nothing else.
That grammar is pinned by exact-string assertions in `test_search.py`, so the
fake cannot quietly drift into being a poor reimplementation of Meilisearch.
"""

# stdlib
import re

FILTER_CLAUSE = re.compile(r'(?P<attribute>\w+) IN \[(?P<values>.*?)\]')
FILTER_VALUE = re.compile(r'"((?:[^"\\]|\\.)*)"|([0-9]+(?:\.[0-9]+)?)')


####################################################################################################
# Parsing the filter grammar back out
####################################################################################################


def parse_filter(expression: str) -> dict:
    """Turn a `build_filter` expression back into `{attribute: [values]}`."""
    parsed = {}
    for clause in FILTER_CLAUSE.finditer(expression or ""):
        values = []
        for quoted, number in FILTER_VALUE.findall(clause.group("values")):
            if quoted:
                values.append(quoted.replace('\\"', '"').replace("\\\\", "\\"))
            else:
                values.append(float(number) if "." in number else int(number))
        parsed[clause.group("attribute")] = values
    return parsed


def matches(document: dict, filters: dict) -> bool:
    """Whether a document satisfies every clause, ORing within each attribute."""
    for attribute, wanted in filters.items():
        held = document.get(attribute)
        held = held if isinstance(held, list) else [held]
        if not set(wanted) & set(held):
            return False
    return True


def has_value(document: dict, attribute: str) -> bool:
    value = document.get(attribute)
    return value is not None and value != ""


def apply_sort(documents: list, terms: list) -> list:
    """Order documents the way Meilisearch would.

    Applied one term at a time, last term first, because Python's sort is
    stable and a descending sort on a string cannot be folded into a single
    key. Documents with no value for an attribute go last whichever direction
    is asked for, which is what Meilisearch does.
    """
    ordered = list(documents)
    for term in reversed(list(terms)):
        attribute, _sep, direction = term.partition(":")
        present = [d for d in ordered if has_value(d, attribute)]
        missing = [d for d in ordered if not has_value(d, attribute)]
        present.sort(key=lambda d, a=attribute: d[a], reverse=direction == "desc")
        ordered = present + missing
    return ordered


####################################################################################################
# The fakes
####################################################################################################


class FakeIndex:
    """Records what the real Meilisearch index would have been asked to do."""

    def __init__(self, documents=None):
        self.settings = {}
        self.added = []
        self.deleted = []
        self.searches = []
        self._documents = list(documents or [])

    ################################################################################################
    # Writing
    ################################################################################################

    def update_settings(self, body):
        self.settings.update(body)

    def add_documents(self, documents, primary_key=None):
        self.added.append((documents, primary_key))
        return {"taskUid": 1}

    def delete_documents(self, ids):
        self.deleted.append(ids)
        return {"taskUid": 2}

    def get_documents(self, parameters=None):
        parameters = parameters or {}
        offset = parameters.get("offset", 0)
        limit = parameters.get("limit", 20)
        page = self._documents[offset : offset + limit]
        return type("Results", (), {"results": page, "total": len(self._documents)})()

    ################################################################################################
    # Reading
    ################################################################################################

    def search(self, query, opt_params=None):
        params = opt_params or {}
        self.searches.append((query, params))

        hits = [d for d in self._documents if self._hit(d, query)]
        hits = [d for d in hits if matches(d, parse_filter(params.get("filter", "")))]

        if params.get("sort"):
            hits = apply_sort(hits, params["sort"])

        distribution = self._facets(hits, params.get("facets") or [])

        offset = params.get("offset", 0)
        limit = params.get("limit", 20)
        window = hits[offset : offset + limit]
        if params.get("attributesToRetrieve"):
            wanted = params["attributesToRetrieve"]
            window = [{k: v for k, v in d.items() if k in wanted} for d in window]

        return {
            "hits": window,
            "estimatedTotalHits": len(hits),
            "facetDistribution": distribution,
        }

    def _hit(self, document, query: str) -> bool:
        """Substring match across every string value, standing in for full text."""
        if not query:
            return True
        haystack = " ".join(
            str(v).lower()
            for value in document.values()
            for v in (value if isinstance(value, list) else [value])
        )
        return query.lower() in haystack

    def _facets(self, hits: list, wanted: list) -> dict:
        distribution = {}
        for attribute in wanted:
            counts = {}
            for document in hits:
                value = document.get(attribute)
                for item in value if isinstance(value, list) else [value]:
                    if item is None or item == "":
                        continue
                    counts[str(item)] = counts.get(str(item), 0) + 1
            distribution[attribute] = counts
        return distribution


class FakeClient:
    def __init__(self, documents=None):
        self.indexes = {}
        self.created = []
        self._documents = documents or []

    def create_index(self, uid, options=None):
        self.created.append((uid, options))

    def index(self, uid):
        if uid not in self.indexes:
            self.indexes[uid] = FakeIndex(self._documents)
        return self.indexes[uid]
