let scientificEvents = [];
const eventsAreItalian = document.documentElement.lang === 'it';
const eventsScriptUrl = document.querySelector('script[src*="events.js"]')?.src || window.location.href;
const eventsDataUrl = new URL('data/scientific-events.json', eventsScriptUrl);
const eventList = document.querySelector('#event-list');
const eventCount = document.querySelector('#event-count');
const eventTypeButtons = document.querySelectorAll('#event-types button');
const eventMore = document.querySelector('#event-load-more');
let activeEventType = '';
let visibleEvents = 12;
const activeEventTheme = new URLSearchParams(window.location.search).get('theme') || '';

const eventThemeNames = {
  interaction: ['Grammar in use and interaction', 'Grammatica nell’uso e nell’interazione'],
  typology: ['Diversity, variation and possibility', 'Diversità, variazione e possibilità'],
  categories: ['Meaning and categories in interaction', 'Significati e categorie nell’interazione'],
  data: ['Data, resources and methods', 'Dati, risorse e metodi']
};

if (eventThemeNames[activeEventTheme]) {
  const themeContext = document.createElement('div');
  themeContext.className = 'event-theme-context';
  themeContext.innerHTML = `<span>${eventsAreItalian ? 'Eventi collegati a' : 'Events related to'} “${eventThemeNames[activeEventTheme][eventsAreItalian ? 1 : 0]}”</span><a href="events.html">${eventsAreItalian ? 'Mostra tutti gli eventi' : 'Show all events'} →</a>`;
  document.querySelector('#event-types')?.insertAdjacentElement('beforebegin', themeContext);
}

const eventTypeNames = {
  conference: ['conference', 'convegno'], workshop: ['workshop / panel', 'workshop / panel'],
  school: ['advanced school', 'scuola avanzata'], series: ['seminar series', 'ciclo seminariale']
};

function escapeEventHtml(value) {
  return String(value || '').replace(/[&<>\"]/g, (character) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[character]));
}

function eventDate(value) {
  if (!eventsAreItalian) return value;
  const months = { Jan: 'gen', Feb: 'feb', Mar: 'mar', Apr: 'apr', May: 'mag', Jun: 'giu', Jul: 'lug', Aug: 'ago', Sep: 'set', Oct: 'ott', Nov: 'nov', Dec: 'dic' };
  return String(value).replace(/\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b/g, (month) => months[month]);
}

function renderEvents() {
  const matches = scientificEvents.filter((item) =>
    (!activeEventType || item.type === activeEventType)
    && (!eventThemeNames[activeEventTheme] || item.themes?.includes(activeEventTheme))
  );
  eventCount.textContent = `${matches.length} ${eventsAreItalian ? (matches.length === 1 ? 'iniziativa' : 'iniziative') : (matches.length === 1 ? 'event' : 'events')}`;
  eventList.innerHTML = matches.slice(0, visibleEvents).map((item) => {
    const copy = eventsAreItalian ? item.it : item.en;
    const title = eventsAreItalian && item.title_it ? item.title_it : item.title;
    const linkLabel = eventsAreItalian ? 'Sito dell’evento' : 'Event website';
    return `<li><span class="talk-year">${escapeEventHtml(eventDate(item.date))}</span><article class="talk-entry event-entry">
      <div class="talk-labels"><span>${escapeEventHtml(eventTypeNames[item.type][eventsAreItalian ? 1 : 0])}</span>${item.forthcoming ? `<span>${eventsAreItalian ? 'prossimamente' : 'forthcoming'}</span>` : ''}</div>
      <h2>${escapeEventHtml(title)}</h2><p>${escapeEventHtml(copy)}</p>
      ${item.url ? `<a class="event-link" href="${escapeEventHtml(item.url)}" target="_blank" rel="noopener">${linkLabel} ↗</a>` : ''}
    </article></li>`;
  }).join('') || `<li class="loading">${eventsAreItalian ? 'Nessuna iniziativa trovata.' : 'No events found.'}</li>`;
  eventMore.hidden = matches.length <= visibleEvents;
}

fetch(eventsDataUrl, { cache: 'no-store' })
  .then((response) => { if (!response.ok) throw new Error(`HTTP ${response.status}`); return response.json(); })
  .then((data) => { scientificEvents = data.events; renderEvents(); })
  .catch(() => { eventList.innerHTML = `<li class="loading">${eventsAreItalian ? 'L’archivio è temporaneamente non disponibile.' : 'The archive is temporarily unavailable.'}</li>`; eventMore.hidden = true; });

eventTypeButtons.forEach((button) => button.addEventListener('click', () => {
  eventTypeButtons.forEach((item) => item.classList.remove('active')); button.classList.add('active');
  activeEventType = button.dataset.type; visibleEvents = 12; renderEvents();
}));
eventMore.addEventListener('click', () => { visibleEvents += 12; renderEvents(); });
