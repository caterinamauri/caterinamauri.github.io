const engagementIsItalian = document.documentElement.lang === 'it';
const engagementTheme = new URLSearchParams(window.location.search).get('theme') || '';
const engagementThemeNames = {
  interaction: ['Grammar, constructions and use', 'Grammatica, costruzioni e uso'],
  typology: ['The world’s languages: typology and variation', 'Le lingue del mondo: tipologia e variazione'],
  categories: ['Categories and meanings in discourse', 'Categorie e significati nel discorso'],
  data: ['Linguistic data and resources', 'Dati e risorse linguistiche']
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
