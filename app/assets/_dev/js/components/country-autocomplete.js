function findMatches(keyword, countries) {
  return countries.filter(country => {
    const regex = new RegExp(keyword, 'gi');
    return country.name.match(regex)
  });
}

// add results to HTML li
function displayMatches() {
    if (countryData) {

      if (this.value.length === 0) {
        suggestions.innerHTML = '';
      } else {
        const matchArray = findMatches(this.value, countryData)
        const html = matchArray.map(country => {
            
            const regex = new RegExp(this.value, 'gi');
            return `
            <li class="country__suggestions_single-country">
                <a href="${country.url}">${country.name}</a>
            </li>
            `;
        }).join('');
        
        suggestions.innerHTML = html;
      }
    }
}

const searchInput = document.querySelector('.country-search__input');
const suggestions = document.querySelector('.country__suggestions');

if (searchInput) {
  searchInput.addEventListener('change', displayMatches);
  searchInput.addEventListener('keyup', displayMatches);
}


