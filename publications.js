let publications = [];
const publicationsAreItalian = document.documentElement.lang === 'it';
const publicationsScriptUrl = document.querySelector('script[src*="publications.js"]')?.src || window.location.href;
const publicationsDataUrl = new URL('data/publications.json', publicationsScriptUrl);
let visiblePublications = 12;
let activePublicationType = '';
const activePublicationTheme = new URLSearchParams(window.location.search).get('theme') || '';
const publicationThemeNames = {
  interaction: ['Grammar in use and interaction', 'Grammatica nell’uso e nell’interazione'],
  typology: ['Diversity, variation and possibility', 'Diversità, variazione e possibilità'],
  categories: ['Meaning and categories in interaction', 'Significati e categorie nell’interazione'],
  data: ['Data, resources and methods', 'Dati, risorse e metodi']
};
const list = document.querySelector('#publication-list');
const search = document.querySelector('#publication-search');
const year = document.querySelector('#publication-year');
const count = document.querySelector('#publication-count');
const more = document.querySelector('#load-more');
const typeButtons = document.querySelectorAll('#publication-types button');
search.value = new URLSearchParams(window.location.search).get('q') || '';
if (publicationThemeNames[activePublicationTheme]) {
  const context = document.createElement('div');
  context.className = 'event-theme-context';
  context.innerHTML = `<span>${publicationsAreItalian ? 'Pubblicazioni collegate a' : 'Publications related to'} “${publicationThemeNames[activePublicationTheme][publicationsAreItalian ? 1 : 0]}”</span><a href="publications.html">${publicationsAreItalian ? 'Mostra tutte le pubblicazioni' : 'Show all publications'} →</a>`;
  document.querySelector('#publication-types')?.insertAdjacentElement('beforebegin', context);
}

function escapeHtml(value) { const element = document.createElement('div'); element.textContent = value ?? ''; return element.innerHTML; }
function apaAuthors(value) {
  const people = String(value || '').split(';').map((name) => name.trim()).filter(Boolean);
  if (people.length < 2) return people[0] || '';
  return `${people.slice(0, -1).join('; ')} & ${people.at(-1)}`;
}
function joinedNames(people) {
  if (!people?.length) return '';
  if (people.length === 1) return people[0];
  return `${people.slice(0, -1).join(', ')} & ${people.at(-1)}`;
}
function chapterSource(item) {
  if (item.type !== 'chapters' || !item.container_title) return '';
  const editorText = item.editors?.length ? `${joinedNames(item.editors)} (${item.editors.length === 1 ? 'Ed.' : 'Eds.'}), ` : '';
  const publicationText = [item.publisher_place, item.publisher].filter(Boolean).join(': ');
  const pages = item.pages ? `, pp. ${String(item.pages).replace(/\s*-\s*/g, '–')}` : '';
  return `In ${editorText}${item.container_title}${publicationText ? `. ${publicationText}` : ''}${pages}.`;
}
function publicationSourceHtml(item) {
  if (item.type === 'chapters' && item.container_title) {
    const editorText = item.editors?.length ? `${joinedNames(item.editors)} (${item.editors.length === 1 ? 'Ed.' : 'Eds.'}), ` : '';
    const publicationText = [item.publisher_place, item.publisher].filter(Boolean).join(': ');
    const pages = item.pages ? `, pp. ${String(item.pages).replace(/\s*-\s*/g, '–')}` : '';
    return `In ${escapeHtml(editorText)}<em>${escapeHtml(item.container_title)}</em>${publicationText ? `. ${escapeHtml(publicationText)}` : ''}${escapeHtml(pages)}.`;
  }
  if (item.type === 'proceedings') {
    const source = conciseSource(item);
    const sourceWithEditors = source.match(/^(In\s+)((?:[A-Z]\.[^,]+,\s*){2})([^,]+)(,.*)$/);
    if (sourceWithEditors) {
      return `${escapeHtml(sourceWithEditors[1] + sourceWithEditors[2])}<em>${escapeHtml(sourceWithEditors[3])}</em>${escapeHtml(sourceWithEditors[4])}`;
    }
    const sourceParts = source.match(/^(In\s+)([^,]+)(,.*)$/);
    if (sourceParts) {
      return `${escapeHtml(sourceParts[1])}<em>${escapeHtml(sourceParts[2])}</em>${escapeHtml(sourceParts[3])}`;
    }
  }
  return escapeHtml(conciseSource(item));
}
function conciseSource(item) {
  const structuredChapter = chapterSource(item);
  if (structuredChapter) return structuredChapter;
  let source = String(item.citation || '');
  const titlePosition = source.toLocaleLowerCase().indexOf(String(item.title || '').toLocaleLowerCase());
  if (titlePosition >= 0) source = source.slice(titlePosition + item.title.length);
  source = source
    .replace(/^\s*[,.:;-]+\s*/, '')
    .replace(/\s*\[[^\]]+\]\s*/g, ' ')
    .replace(/\s*Open Access\s*/gi, ' ')
    .replace(/\s*\(atti di:[^)]+\)/gi, '')
    .replace(/\s*@\s*LREC\b.*$/i, '')
    .replace(/[«»]/g, '')
    .replace(new RegExp(`,\\s*${item.year}\\s*,`, 'g'), ',')
    .replace(/\bpp\.\s*(\d+)\s*-\s*(\d+)/gi, 'pp. $1–$2')
    .replace(/\s+,/g, ',')
    .replace(/\s+/g, ' ')
    .replace(/^in:\s*/i, 'In ')
    .trim();
  return source.replace(/[.,;:\s]+$/, '') + (source ? '.' : '');
}
function renderPublications() {
  if (!publications.length) return;
  const query = search.value.trim().toLowerCase();
  const matches = publications.filter((item) => (!year.value || String(item.year) === year.value) && (!activePublicationType || item.type === activePublicationType) && (!publicationThemeNames[activePublicationTheme] || item.themes?.includes(activePublicationTheme)) && (!query || `${item.title} ${item.authors} ${item.citation}`.toLowerCase().includes(query)));
  count.textContent = `${matches.length} ${publicationsAreItalian ? 'pubblicazioni' : 'publications'}`;
  list.innerHTML = matches.slice(0, visiblePublications).map((item) => `<li><div class="apa-entry"><p class="apa-authors">${escapeHtml(apaAuthors(item.authors))} (${item.year || 'n.d.'}).</p><h3><a href="${item.url}" target="_blank" rel="noopener">${escapeHtml(item.title)}</a>${item.open_access ? `<span class="oa">${publicationsAreItalian ? 'Accesso aperto' : 'Open access'}</span>` : ''}</h3><p class="apa-source">${publicationSourceHtml(item)}</p></div></li>`).join('') || `<li class="loading">${publicationsAreItalian ? 'Nessun risultato.' : 'No results.'}</li>`;
  more.hidden = visiblePublications >= matches.length;
}
fetch(publicationsDataUrl, { cache: 'no-store' }).then((response) => { if (!response.ok) throw new Error(`HTTP ${response.status}`); return response.json(); }).then((data) => { publications = data.publications; [...new Set(publications.map((item) => item.year).filter(Boolean))].sort((a,b) => b-a).forEach((value) => year.add(new Option(value,value))); renderPublications(); }).catch(() => { list.innerHTML = `<li class="loading">${publicationsAreItalian ? 'Archivio delle pubblicazioni non disponibile.' : 'Publication archive unavailable.'}</li>`; more.hidden = true; });
[search, year].forEach((control) => control.addEventListener('input', () => { visiblePublications = 12; renderPublications(); }));
typeButtons.forEach((button) => button.addEventListener('click', () => { activePublicationType = button.dataset.type; typeButtons.forEach((item) => item.classList.toggle('active', item === button)); visiblePublications = 12; renderPublications(); }));
more.addEventListener('click', () => { visiblePublications += 12; renderPublications(); });
