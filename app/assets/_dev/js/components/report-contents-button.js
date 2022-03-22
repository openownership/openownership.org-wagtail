var reportContentsButton = document.getElementById('report-contents');
if (reportContentsButton) {

    var leftMenu = document.getElementById('page-menu');

    reportContentsButton.addEventListener('click', (e) => {
        e.preventDefault();
        
        reportContentsButton.classList.toggle('expanded');
        leftMenu.classList.toggle('show');
        
        if (reportContentsButton.classList.contains('expanded')) {
            reportContentsButton.setAttribute('aria-expanded', true);
            
        } else {
            reportContentsButton.setAttribute('aria-expanded', false);
         
        }
    }); 
}

