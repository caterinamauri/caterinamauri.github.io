const menuButton = document.querySelector('.nav-toggle');
const navigation = document.querySelector('#main-nav');

menuButton?.addEventListener('click', () => {
  const isOpen = navigation.classList.toggle('open');
  menuButton.setAttribute('aria-expanded', String(isOpen));
});

navigation?.addEventListener('click', () => {
  navigation.classList.remove('open');
  menuButton?.setAttribute('aria-expanded', 'false');
});

const publicationList = document.querySelector('#recent-publications');

function publicationYear(item) {
  const value = Number.parseInt(item.year, 10);
  return Number.isFinite(value) ? value : 0;
}

fetch('../../data/publications.json')
  .then(response => {
    if (!response.ok) throw new Error('Publication data unavailable');
    return response.json();
  })
  .then(data => {
    const records = Array.isArray(data) ? data : (data.publications || []);
    const recent = records
      .slice()
      .sort((a, b) => publicationYear(b) - publicationYear(a))
      .slice(0, 5);

    publicationList.replaceChildren(...recent.map(item => {
      const entry = document.createElement('li');
      const year = document.createElement('span');
      const title = item.url ? document.createElement('a') : document.createElement('span');
      const meta = document.createElement('p');
      year.className = 'year';
      year.textContent = item.year || 'Forthcoming';
      title.className = 'title';
      title.textContent = item.title || 'Untitled publication';
      if (item.url) title.href = item.url;
      meta.className = 'meta';
      meta.textContent = [item.authors || item.author, item.venue || item.journal || item.publisher]
        .filter(Boolean)
        .join(' · ');
      entry.append(year, title, meta);
      return entry;
    }));
  })
  .catch(() => {
    publicationList.innerHTML = '<li class="loading">Open the complete publication archive.</li>';
  });
