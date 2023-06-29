var giveFeedbackButton = document.getElementById('give-feedback');
var feedbackForm = document.getElementById('feedback-form');

var textAreaWhyOther = document.getElementById('text-area-why-other');
var textAreaWhereOther = document.getElementById('text-area-where-other');

var whyOtherRadioButton = document.getElementById('id_why_downloading_4');
var whereOtherRadioButton = document.getElementById('id_where_downloading_4');

var successMessage = document.getElementById('success-message');
var dismissMessage = document.getElementById('dismiss-success-message');

if (giveFeedbackButton) {
    giveFeedbackButton.addEventListener('click', (e) => {
        e.preventDefault();
        giveFeedbackButton.classList.toggle('expanded');

        // check if "other" is selected in the "why" feedback and show/hide the text area field
        var whyDownloadingHandler = function expandCollapseOtherField(event) {
            if (document.querySelector('input[name="why_downloading"]:checked').value === 'other') {
                if (!textAreaWhyOther.classList.contains('expanded')) {
                    textAreaWhyOther.classList.add('expanded');
                }
            } else {
                if (textAreaWhyOther.classList.contains('expanded')) {
                    textAreaWhyOther.classList.remove('expanded');
                }
            }
        }

        // check if "other" is selected in the "where" feedback and show/hide the text area field
        var whereWorkerHandler = function expandCollapseOtherField(event) {
            if (document.querySelector('input[name="where_work"]:checked').value === 'other') {
                if (!textAreaWhereOther.classList.contains('expanded')) {
                    textAreaWhereOther.classList.add('expanded');
                }
            } else {
                if (textAreaWhereOther.classList.contains('expanded')) {
                    textAreaWhereOther.classList.remove('expanded');
                }
            }
        }
        
        //show/hide form
        if (giveFeedbackButton.classList.contains('expanded')) {
            
            giveFeedbackButton.setAttribute('aria-expanded', true);
            feedbackForm.classList.remove('collapsed');

            // remove success message if a new form is opened
            if (successMessage && !successMessage.classList.contains('collapsed')) {
                successMessage.classList.add('collapsed');
            }

            //attach event listener to the radio buttons and check if "other" was chosen
            document.querySelectorAll("input[name='why_downloading']").forEach((input) => {
                if (!input.getAttribute('data-event-listener')) {
                    input.setAttribute('data-event-listener', 'true');
                    input.addEventListener('change', whyDownloadingHandler, true);
                }
            });

            document.querySelectorAll("input[name='where_work']").forEach((input) => {
                if (!input.getAttribute('data-event-listener')) {
                    input.setAttribute('data-event-listener', 'true');
                    input.addEventListener('change', whereWorkerHandler, true);
                }
            });

        } else {
            giveFeedbackButton.setAttribute('aria-expanded', false);

            //remove event listeners
            document.querySelectorAll("input[name='why_downloading']").forEach((input) => {
                input.setAttribute('data-event-listener', 'false');
                input.removeEventListener('change', whyDownloadingHandler, true);
            });

            document.querySelectorAll("input[name='where_work']").forEach((input) => {
                input.setAttribute('data-event-listener', 'false');
                input.removeEventListener('change', whereWorkerHandler, true);
            });

            feedbackForm.classList.add('collapsed');
        }
    }); 
}

if (successMessage) {
    dismissMessage.addEventListener('click', (e) => {
        e.preventDefault();
        successMessage.classList.add('collapsed');
    });
}
