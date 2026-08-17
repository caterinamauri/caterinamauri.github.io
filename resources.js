let resources = [];
const resourcesAreItalian = document.documentElement.lang === 'it';
const resourcesScriptUrl = document.querySelector('script[src*="resources.js"]')?.src || window.location.href;
const resourcesDataUrl = new URL('data/resources.json', resourcesScriptUrl);
const resourceList = document.querySelector('#resource-list');
const resourceSearch = document.querySelector('#resource-search');
const resourceYear = document.querySelector('#resource-year');
const resourceCount = document.querySelector('#resource-count');
resourceSearch.value = new URLSearchParams(window.location.search).get('q') || '';

function escapeResourceHtml(value) {
  const element = document.createElement('div');
  element.textContent = value ?? '';
  return element.innerHTML;
}

function renderResources() {
  const query = resourceSearch.value.trim().toLowerCase();
  const matches = resources.filter((item) =>
    (!resourceYear.value || String(item.year) === resourceYear.value)
    && (!query || `${item.title} ${item.authors} ${item.citation}`.toLowerCase().includes(query))
  );
  resourceCount.textContent = `${matches.length} ${resourcesAreItalian ? (matches.length === 1 ? 'risorsa' : 'risorse') : (matches.length === 1 ? 'resource' : 'resources')}`;
  resourceList.innerHTML = matches.map((item) => {
    const source = item.source || (item.link_type === 'official_resource' ? 'Universal Dependencies' : 'Unibo IRIS');
    const linkLabel = resourcesAreItalian
      ? (item.link_type === 'iris' ? 'Scheda IRIS ↗' : 'Apri la risorsa ↗')
      : (item.link_label || (item.link_type === 'iris' ? 'IRIS record ↗' : 'Open resource ↗'));
    const secondaryLink = item.secondary_url
      ? `<a href="${item.secondary_url}" target="_blank" rel="noopener">${escapeResourceHtml(resourcesAreItalian ? 'Risorsa ufficiale ↗' : (item.secondary_link_label || 'Official resource ↗'))}</a>`
      : '';
    return `
    <li>
      <span class="resource-year">${item.year || '—'}</span>
      <div class="resource-entry">
        <h2><a href="${item.url}" target="_blank" rel="noopener">${escapeResourceHtml(item.title)}</a></h2>
        <p>${escapeResourceHtml(item.citation)}</p>
        <div class="resource-entry-meta"><span>${escapeResourceHtml(source)}</span><div class="resource-entry-links"><a href="${item.url}" target="_blank" rel="noopener">${escapeResourceHtml(linkLabel)}</a>${secondaryLink}</div></div>
      </div>
    </li>`;
  }).join('') || '<li class="loading">No resources found.</li>';
}

fetch(resourcesDataUrl, { cache: 'no-store' })
  .then((response) => { if (!response.ok) throw new Error(`HTTP ${response.status}`); return response; })
  .then((response) => response.json())
  .then((data) => {
    resources = data.resources;
    [...new Set(resources.map((item) => item.year).filter(Boolean))]
      .sort((a, b) => b - a)
      .forEach((value) => resourceYear.add(new Option(value, value)));
    renderResources();
  })
  .catch(() => {
    resourceList.innerHTML = `<li class="loading">${resourcesAreItalian ? 'L’archivio delle risorse è temporaneamente non disponibile.' : 'The resource archive is temporarily unavailable.'}</li>`;
  });

[resourceSearch, resourceYear].forEach((control) => control.addEventListener('input', renderResources));
