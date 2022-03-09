var secondaryLevelButtons = document.querySelectorAll('.--level-two');

secondaryLevelButtons.forEach(function(button) {
    button.addEventListener('click', function(){
        let submenu = button.nextElementSibling;
        var parentLi = button.parentElement;

        if (submenu.classList.contains('subnav--hidden')) {
          this.setAttribute('aria-expanded', 'true');
          this.classList.add('expanded');
          submenu.classList.remove('subnav--hidden');
          parentLi.classList.add('expanded');
        } else {
          submenu.classList.add('subnav--hidden'); 
          parentLi.classList.remove('expanded');
          this.classList.remove('expanded');
          this.setAttribute('aria-expanded', 'false');
        }
      });
      
});

var firstLevelButtons = document.querySelectorAll('.--level-one');

firstLevelButtons.forEach(function(button) {
    button.addEventListener('click', function(){
        let submenu = button.nextElementSibling;
        var parentLi = button.parentElement;
  
        if (submenu.classList.contains('subnav--hidden')) {
          this.setAttribute('aria-expanded', 'true');
          this.classList.add('expanded');
          submenu.classList.remove('subnav--hidden');
          parentLi.classList.add('expanded');
        } else {
          submenu.classList.add('subnav--hidden'); 
          parentLi.classList.remove('expanded');
          this.classList.remove('expanded');
          this.setAttribute('aria-expanded', 'false');
        }
      });
      
});

var mobileToggle = document.querySelector('.navigation__toggle');

mobileToggle.addEventListener('click', function(){
  let mainMenu = this.nextElementSibling;
  if (mainMenu.classList.contains('--hidden')) {
    this.setAttribute('aria-expanded', 'true');
    this.classList.add('expanded');
    mainMenu.classList.remove('--hidden');
  } else {
    mainMenu.classList.add('--hidden'); 
    this.classList.remove('expanded');
    this.setAttribute('aria-expanded', 'false');
  }
});

