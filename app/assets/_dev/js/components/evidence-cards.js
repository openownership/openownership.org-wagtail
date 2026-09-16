/*
 * BOT Evidence Centre: keep one record open at a time, and keep the keyboard.
 *
 * Opening a record swaps its card for the open version, so the shut markup is
 * gone once htmx has run. It is kept here instead, which means shutting the
 * others costs no extra request and cannot race the opening one for the URL in
 * the address bar.
 *
 * Swapping a card also destroys the element that was clicked, which drops focus
 * to the top of the document. That is the difference between this being usable
 * and unusable from a keyboard, so focus is moved deliberately after every swap:
 * into the record on opening, back to its own control on closing.
 *
 * Everything here is an enhancement. With JavaScript off the same links still
 * work, one record per page load.
 */

var shutCards = new Map();
var pending = null;

function isEvidenceCard(node) {
    return node && node.classList && node.classList.contains('evidence-card');
}

function focus(element) {
    if (element) {
        element.focus();
    }
}

document.body.addEventListener('htmx:beforeSwap', (event) => {
    var card = event.detail.target;

    if (!isEvidenceCard(card) || !card.id) {
        pending = null;
        return;
    }

    if (!card.classList.contains('evidence-card--expanded')) {
        shutCards.set(card.id, card.outerHTML);
    }

    /* Which way this swap goes has to be read from the response. htmx reports
       the element it is about to replace, so the card's own classes still
       describe the state being left behind, not the one arriving. */
    pending = {
        id: card.id,
        opening: event.detail.serverResponse.indexOf('evidence-card--expanded') !== -1,
    };
});

document.body.addEventListener('htmx:afterSwap', () => {
    if (!pending) {
        return;
    }

    var swap = pending;
    pending = null;

    var card = document.getElementById(swap.id);
    if (!card) {
        return;
    }

    if (!swap.opening) {
        /* Closing: hand the keyboard back to the control that did it, which is
           now the shut card's own "Read more". */
        focus(card.querySelector('.evidence-card__toggle a'));
        return;
    }

    shutOthers(swap.id);

    /* Opening: focus the record's heading rather than the close link, so the
       reader hears which record they opened before its controls. */
    focus(card.querySelector('.card-group__title'));
});

function shutOthers(openId) {
    document.querySelectorAll('.evidence-card--expanded').forEach((card) => {
        if (card.id === openId) {
            return;
        }

        var markup = shutCards.get(card.id);
        if (!markup) {
            return;
        }

        card.outerHTML = markup;
        window.htmx.process(document.getElementById(card.id));
    });
}

/* The control is a plain link until JavaScript arrives, at which point it starts
   behaving as a disclosure. `aria-expanded` is set here rather than in the
   template for exactly that reason: without JavaScript it would be a lie. */
function markToggles(root) {
    (root || document).querySelectorAll('.evidence-card').forEach((card) => {
        var toggle = card.querySelector('.evidence-card__toggle a');
        if (toggle) {
            toggle.setAttribute(
                'aria-expanded',
                card.classList.contains('evidence-card--expanded') ? 'true' : 'false',
            );
        }
    });
}

markToggles();
document.body.addEventListener('htmx:afterSettle', () => markToggles());
