let talks = [];
const talksAreItalian = document.documentElement.lang === 'it';
const talksScriptUrl = document.querySelector('script[src*="talks.js"]')?.src || window.location.href;
const talksDataUrl = new URL('data/talks.json', talksScriptUrl);
let activeTalkType = '';
let visibleTalks = 18;
const activeTalkTheme = new URLSearchParams(window.location.search).get('theme') || '';
const talkThemeNames = {
  interaction: ['Grammar in use and interaction', 'Grammatica nell’uso e nell’interazione'],
  typology: ['Diversity, variation and possibility', 'Diversità, variazione e possibilità'],
  categories: ['Meaning and categories in interaction', 'Significati e categorie nell’interazione'],
  data: ['Data, resources and methods', 'Dati, risorse e metodi']
};

const talkList = document.querySelector('#talk-list');
const talkSearch = document.querySelector('#talk-search');
const talkYear = document.querySelector('#talk-year');
const talkCount = document.querySelector('#talk-count');
const talkTypeButtons = document.querySelectorAll('#talk-types button');
const talkMore = document.querySelector('#talk-load-more');
talkSearch.value = new URLSearchParams(window.location.search).get('q') || '';

if (talkThemeNames[activeTalkTheme]) {
  const context = document.createElement('div');
  context.className = 'event-theme-context';
  context.innerHTML = `<span>${talksAreItalian ? 'Talks collegati a' : 'Talks related to'} “${talkThemeNames[activeTalkTheme][talksAreItalian ? 1 : 0]}”</span><a href="talks.html">${talksAreItalian ? 'Mostra tutti i talks' : 'Show all talks'} →</a>`;
  document.querySelector('#talk-types')?.insertAdjacentElement('beforebegin', context);
}

function escapeTalkHtml(value) {
  return String(value || '').replace(/[&<>"]/g, (character) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[character]));
}

function talkDetailsHtml(item) {
  let details = String(item.citation || '');
  const quotedTitle = `“${item.title}”`;
  let authors = '';
  if (details.includes(quotedTitle)) {
    const parts = details.split(quotedTitle);
    authors = parts.shift().replace(/^Forthcoming\.\s*/, '').trim();
    details = parts.join(quotedTitle);
  } else if (details.startsWith(`${item.title}.`)) {
    details = details.slice(item.title.length + 1);
  }
  details = details.replace(/\.\s*\./g, '.').replace(/\s{2,}/g, ' ').replace(/^\s*[,.]\s*/, '').trim();
  const authorHtml = authors ? `${escapeTalkHtml(authors)} ` : '';
  let detailsHtml = escapeTalkHtml(details);
  if (item.event) {
    const escapedEvent = escapeTalkHtml(item.event);
    detailsHtml = detailsHtml.replace(escapedEvent, `<em>${escapedEvent}</em>`);
  }
  return `${authorHtml}${detailsHtml}`;
}

function renderTalks() {
  const query = talkSearch.value.trim().toLowerCase();
  const matches = talks.filter((item) =>
    (!talkYear.value || String(item.year) === talkYear.value)
    && (!activeTalkType || item.type === activeTalkType)
    && (!talkThemeNames[activeTalkTheme] || item.themes?.includes(activeTalkTheme))
    && (!query || `${item.title} ${item.citation}`.toLowerCase().includes(query))
  );
  talkCount.textContent = `${matches.length} ${talksAreItalian ? (matches.length === 1 ? 'intervento' : 'interventi') : (matches.length === 1 ? 'talk' : 'talks')}`;
  talkList.innerHTML = matches.slice(0, visibleTalks).map((item) => `
    <li>
      <span class="talk-year">${item.year}</span>
      <article class="talk-entry">
        <div class="talk-labels"><span>${item.type === 'selected' ? (talksAreItalian ? 'da call' : 'refereed') : (talksAreItalian ? 'su invito' : 'invited')}</span>${item.forthcoming ? `<span>${talksAreItalian ? 'prossimamente' : 'forthcoming'}</span>` : ''}</div>
        <h2>${escapeTalkHtml(item.title)}</h2>
        <p>${talkDetailsHtml(item)}</p>
      </article>
    </li>
  `).join('') || `<li class="loading">${talksAreItalian ? 'Nessun intervento trovato.' : 'No talks found.'}</li>`;
  talkMore.hidden = matches.length <= visibleTalks;
}

fetch(talksDataUrl, { cache: 'no-store' })
  .then((response) => { if (!response.ok) throw new Error(`HTTP ${response.status}`); return response; })
  .then((response) => response.json())
  .then((data) => {
    talks = data.talks;
    [...new Set(talks.map((item) => item.year))].sort((a, b) => b - a).forEach((value) => talkYear.add(new Option(value, value)));
    renderTalks();
  })
  .catch(() => { talkList.innerHTML = `<li class="loading">${talksAreItalian ? 'L’archivio degli interventi è temporaneamente non disponibile.' : 'The talk archive is temporarily unavailable.'}</li>`; talkMore.hidden = true; });

[talkSearch, talkYear].forEach((control) => control.addEventListener('input', () => { visibleTalks = 18; renderTalks(); }));
talkTypeButtons.forEach((button) => button.addEventListener('click', () => {
  talkTypeButtons.forEach((item) => item.classList.remove('active'));
  button.classList.add('active');
  activeTalkType = button.dataset.type;
  visibleTalks = 18;
  renderTalks();
}));
talkMore.addEventListener('click', () => { visibleTalks += 18; renderTalks(); });
