const engagementIsItalian = document.documentElement.lang === 'it';
const engagementTheme = new URLSearchParams(window.location.search).get('theme') || '';
const engagementThemeNames = {
  interaction: ['Grammar in use and interaction', 'Grammatica nell’uso e nell’interazione'],
  typology: ['Linguistic diversity, typology and variation', 'Diversità linguistica, tipologia e variazione'],
  categories: ['Categories, meaning and shared understanding', 'Categorie, significato e comprensione condivisa'],
  data: ['Data, resources and methods', 'Dati, risorse e metodi']
};

if (engagementThemeNames[engagementTheme]) {
  const themeContext = document.createElement('div');
  themeContext.className = 'engagement-theme-context';
  themeContext.innerHTML = `<span>${engagementIsItalian ? 'Attività collegate a' : 'Activities related to'} “${engagementThemeNames[engagementTheme][engagementIsItalian ? 1 : 0]}”</span><a href="engagement.html">${engagementIsItalian ? 'Mostra tutte le attività' : 'Show all activities'} →</a>`;
  document.querySelector('.teaching-hero')?.insertAdjacentElement('afterend', themeContext);

  document.querySelectorAll('[data-theme-section]').forEach((section) => {
    const entries = [...section.querySelectorAll('article')];
    entries.forEach((entry) => {
      entry.hidden = !(entry.dataset.themes || '').split(/\s+/).includes(engagementTheme);
    });
    section.hidden = entries.every((entry) => entry.hidden);
  });
}
