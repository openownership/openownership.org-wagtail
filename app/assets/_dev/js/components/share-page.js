var sharePageButton = document.getElementById('share-page');
var sharePageLinks = document.getElementById('share-page-links');

sharePageButton.addEventListener('click', (e) => {
    e.preventDefault();
    
    sharePageButton.classList.toggle('expanded');

    sharePageLinks.classList.toggle('collapsed');

    if (sharePageButton.classList.contains('expanded')) {
        sharePageButton.setAttribute('aria-expanded', true);
        
    } else {
        sharePageButton.setAttribute('aria-expanded', false);
     
    }
  })

