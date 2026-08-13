let resources = [];
const resourceList = document.querySelector('#resource-list');
const resourceSearch = document.querySelector('#resource-search');
const resourceYear = document.querySelector('#resource-year');
const resourceCount = document.querySelector('#resource-count');

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
  resourceCount.textContent = `${matches.length} ${matches.length === 1 ? 'resource' : 'resources'}`;
  resourceList.innerHTML = matches.map((item) => {
    const source = item.source || (item.link_type === 'official_resource' ? 'Universal Dependencies' : 'Unibo IRIS');
    const linkLabel = item.link_label || 'Open resource ↗';
    return `
    <li>
      <span class="resource-year">${item.year || '—'}</span>
      <div class="resource-entry">
        <h2><a href="${item.url}" target="_blank" rel="noopener">${escapeResourceHtml(item.title)}</a></h2>
        <p>${escapeResourceHtml(item.citation)}</p>
        <div class="resource-entry-meta"><span>${escapeResourceHtml(source)}</span><a href="${item.url}" target="_blank" rel="noopener">${escapeResourceHtml(linkLabel)}</a></div>
      </div>
    </li>`;
  }).join('') || '<li class="loading">No resources found.</li>';
}

fetch('data/resources.json')
  .then((response) => response.json())
  .then((data) => {
    resources = data.resources;
    [...new Set(resources.map((item) => item.year).filter(Boolean))]
      .sort((a, b) => b - a)
      .forEach((value) => resourceYear.add(new Option(value, value)));
    renderResources();
  })
  .catch(() => {
    resourceList.innerHTML = '<li class="loading">The resource archive is temporarily unavailable.</li>';
  });

[resourceSearch, resourceYear].forEach((control) => control.addEventListener('input', renderResources));
