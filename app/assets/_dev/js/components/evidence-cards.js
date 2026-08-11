/*
 * BOT Evidence Centre: keep one record open at a time.
 *
 * Opening a record swaps its card for the open version, so the shut markup is
 * gone once htmx has run. It is kept here instead, which means shutting the
 * others costs no extra request and cannot race the opening one for the URL in
 * the address bar.
 *
 * Everything here is an enhancement. With JavaScript off the same links still
 * work, one record per page load.
 */

var shutCards = new Map();
var openingId = null;

function isEvidenceCard(node) {
    return node && node.classList && node.classList.contains('evidence-card');
}

document.body.addEventListener('htmx:beforeSwap', (event) => {
    var card = event.detail.target;

    if (!isEvidenceCard(card) || !card.id) {
        return;
    }

    if (!card.classList.contains('evidence-card--expanded')) {
        shutCards.set(card.id, card.outerHTML);
    }

    /* Which way this swap goes has to be read from the response. htmx reports
       the element it is about to replace, so the card's own classes still
       describe the state being left behind, not the one arriving. */
    openingId = event.detail.serverResponse.indexOf('evidence-card--expanded') === -1
        ? null
        : card.id;
});

document.body.addEventListener('htmx:afterSwap', () => {
    if (!openingId) {
        return;
    }

    var opened = openingId;
    openingId = null;

    document.querySelectorAll('.evidence-card--expanded').forEach((card) => {
        if (card.id === opened) {
            return;
        }

        var markup = shutCards.get(card.id);
        if (!markup) {
            return;
        }

        card.outerHTML = markup;
        window.htmx.process(document.getElementById(card.id));
    });
});
