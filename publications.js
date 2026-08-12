let publications = [];
let visiblePublications = 12;
let activePublicationType = '';
const list = document.querySelector('#publication-list');
const search = document.querySelector('#publication-search');
const year = document.querySelector('#publication-year');
const count = document.querySelector('#publication-count');
const more = document.querySelector('#load-more');
const typeButtons = document.querySelectorAll('#publication-types button');

function escapeHtml(value) { const element = document.createElement('div'); element.textContent = value ?? ''; return element.innerHTML; }
function renderPublications() {
  if (!publications.length) return;
  const query = search.value.trim().toLowerCase();
  const matches = publications.filter((item) => (!year.value || String(item.year) === year.value) && (!activePublicationType || item.type === activePublicationType) && (!query || `${item.title} ${item.authors} ${item.citation}`.toLowerCase().includes(query)));
  count.textContent = `${matches.length} publications`;
  list.innerHTML = matches.slice(0, visiblePublications).map((item) => `<li><span class="year">${item.year || '—'}</span><div><h3><a href="${item.url}" target="_blank" rel="noopener">${escapeHtml(item.title)}</a>${item.open_access ? '<span class="oa">Open access</span>' : ''}</h3><p>${escapeHtml(item.citation)}</p></div></li>`).join('') || '<li class="loading">No results.</li>';
  more.hidden = visiblePublications >= matches.length;
}
fetch('data/publications.json').then((response) => response.json()).then((data) => { publications = data.publications; [...new Set(publications.map((item) => item.year).filter(Boolean))].sort((a,b) => b-a).forEach((value) => year.add(new Option(value,value))); renderPublications(); }).catch(() => { list.innerHTML = '<li class="loading">Publication archive unavailable.</li>'; more.hidden = true; });
[search, year].forEach((control) => control.addEventListener('input', () => { visiblePublications = 12; renderPublications(); }));
typeButtons.forEach((button) => button.addEventListener('click', () => { activePublicationType = button.dataset.type; typeButtons.forEach((item) => item.classList.toggle('active', item === button)); visiblePublications = 12; renderPublications(); }));
more.addEventListener('click', () => { visiblePublications += 12; renderPublications(); });
