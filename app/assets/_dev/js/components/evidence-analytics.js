/*
 * BOT Evidence Centre: the custom events Open Ownership asked for.
 *
 * Most of the twelve metrics in the sprint brief are native Plausible. Three are
 * not, and are sent from here:
 *
 *   Evidence: Search        how often people search, and how many results they got
 *   Evidence: Filter        which facet was used, and which value
 *   Evidence: Source click  an outbound click, broken down by topic/jurisdiction/region
 *
 * Total outbound clicks are counted by Plausible's outbound-links extension on
 * its own. The event here adds the breakdown on top of that count.
 *
 * `window.plausible` is defined in the analytics partial before the script
 * loads, so calling it here is safe even if the script has not arrived, and
 * safe in development where the script is never loaded at all.
 */

var STORAGE_PREFIX = 'evidence-analytics:';

function send(name, props) {
    if (typeof window.plausible !== 'function') {
        return;
    }
    window.plausible(name, { props: props });
}

/* Filters and searches survive a page load, so the events are read off the page
   rather than fired on a click. Paging through the same results would otherwise
   count the filter again on every page, so the page number is dropped and the
   rest of the query remembered for the session. */
function alreadyCounted() {
    var params = new URLSearchParams(window.location.search);
    params.delete('page');
    var key = STORAGE_PREFIX + params.toString();

    try {
        if (window.sessionStorage.getItem(key)) {
            return true;
        }
        window.sessionStorage.setItem(key, '1');
    } catch (err) {
        /* Private browsing can refuse storage. Counting twice is better than
           losing the event entirely. */
        return false;
    }

    return false;
}

function resultCount(results) {
    var total = parseInt(results.getAttribute('data-evidence-total'), 10);
    return isNaN(total) ? 0 : total;
}

function reportSearch(results) {
    var input = document.getElementById('evidence-q');
    var terms = input && input.value.trim();
    if (!terms) {
        return;
    }

    var props = { results: resultCount(results) };

    /* Whether the term itself is recorded is Open Ownership's call, so it is a
       setting rather than something baked in here. */
    if (results.getAttribute('data-evidence-record-terms') === 'true') {
        props.term = terms.toLowerCase();
    }

    send('Evidence: Search', props);
}

/* Read from the ticked boxes rather than the URL, so the list of facets lives
   in one place: the filter form the server rendered. */
function reportFilters() {
    var ticked = document.querySelectorAll('.evidence-filters input[type=checkbox]:checked');

    ticked.forEach((input) => {
        send('Evidence: Filter', { facet: input.name, value: input.value });
    });
}

function reportOutboundClick(link) {
    send('Evidence: Source click', {
        topic: link.getAttribute('data-topic') || '(none)',
        jurisdiction: link.getAttribute('data-jurisdiction') || '(none)',
        region: link.getAttribute('data-region') || '(none)',
    });
}

/* Searches and filters only happen on the listing, which is the only page
   carrying a result count. */
var results = document.querySelector('[data-evidence-total]');

if (results && !alreadyCounted()) {
    reportSearch(results);
    reportFilters();
}

/* Outbound clicks happen on the listing and on a record's own page. Delegated,
   so a card htmx has just swapped in is covered without rebinding. */
document.body.addEventListener('click', (event) => {
    var link = event.target.closest('a[data-topic]');
    if (link) {
        reportOutboundClick(link);
    }
});
