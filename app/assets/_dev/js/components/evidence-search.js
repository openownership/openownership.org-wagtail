/*
 * BOT Evidence Centre: make the search field's own clear button do something.
 *
 * A `type="search"` field gets an "x" from the browser. It empties the box and
 * submits nothing, so before this a reader had to press Apply as well, which is
 * two steps for one intention.
 *
 * The `search` event fires when that control is used, so this follows the
 * "Clear search" link instead of submitting the form. Both routes then land on
 * exactly the same URL, and it is the tidier of the two: submitting the form
 * posts every empty field back as well.
 *
 * Only when the box has actually been emptied: the same event fires when a
 * reader presses Enter, which the form already handles.
 *
 * This is an enhancement. The link does the same job in one click with no
 * JavaScript at all, and is the only route in a browser that draws no clear
 * button, Firefox among them.
 */

var evidenceSearch = document.getElementById('evidence-q');
var evidenceClearSearch = document.querySelector('.evidence-filters__clear-search');

if (evidenceSearch && evidenceClearSearch) {
    evidenceSearch.addEventListener('search', () => {
        if (evidenceSearch.value === '') {
            window.location.href = evidenceClearSearch.href;
        }
    });
}
