/*------------------------------------*\
  #CSS
\*------------------------------------*/

import '../css/main.css';

document.querySelector('html').classList.remove('no-js');


/*------------------------------------*\
  #HTMX
\*------------------------------------*/

/* Assigned to window as well as imported, so that hx-on handlers in templates
   and any htmx extension we add later can find it. Everything built with it
   has to keep working without it: htmx enhances markup that already works as
   plain links and forms. */
import htmx from 'htmx.org';

window.htmx = htmx;

import './components/share-page.js';
import './components/glossary.js';
import './components/navigation.js';

import './components/map.js';

import './components/country-autocomplete.js';

import './components/report-contents-button.js';
import './components/feedback-form.js';
import './components/evidence-cards.js';
import './components/evidence-search.js';
import './components/evidence-analytics.js';
