var giveFeedbackButton = document.getElementById('give-feedback');
var feedbackForm = document.getElementById('feedback-form');

if (giveFeedbackButton) {
    giveFeedbackButton.addEventListener('click', (e) => {
        e.preventDefault();
        
        giveFeedbackButton.classList.toggle('expanded');
    
        feedbackForm.classList.toggle('collapsed');
    
        if (giveFeedbackButton.classList.contains('expanded')) {
            giveFeedbackButton.setAttribute('aria-expanded', true);
            
        } else {
            giveFeedbackButton.setAttribute('aria-expanded', false);
         
        }
    }); 
}

