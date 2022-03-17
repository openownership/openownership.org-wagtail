const accordionButtons = document.querySelectorAll('.accordion__button');
const accordionSections = document.querySelectorAll('.accordion__section');

accordionSections.forEach(section =>  {
  section.setAttribute('aria-hidden', true)
  section.classList.remove('open')
})

accordionButtons.forEach(button => {
  button.setAttribute('aria-expanded', false);
  
  const expanded = button.getAttribute('aria-expanded');
  const number = button.getAttribute('id').split('accordion-open-').pop();
  const associatedSection = document.getElementById(`accordion-section-${number}`)
 
  button.addEventListener('click', () => {
    
    button.classList.toggle('expanded');
    associatedSection.classList.toggle('open');
    if (button.classList.contains('expanded')) {
      button.setAttribute('aria-expanded', true);
      associatedSection.setAttribute('aria-hidden', false);
    } else {
      button.setAttribute('aria-expanded', false);
      associatedSection.setAttribute('aria-hidden', true);
    }
  })
})

