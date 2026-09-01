const siteIsItalian = document.documentElement.lang === 'it';
document.querySelectorAll('[data-current-year]').forEach((element) => { element.textContent = new Date().getFullYear(); });

const canonicalOrigin = 'https://caterinamauri.github.io';
const pagePath = window.location.pathname.replace(/\/index\.html$/, '/');
const canonicalUrl = `${canonicalOrigin}${pagePath}`;
const isIndexable = !document.querySelector('meta[name="robots"][content*="noindex"]');
const alternatePath = siteIsItalian
  ? pagePath.replace(/^\/it\//, '/')
  : (pagePath === '/' ? '/it/' : `/it${pagePath}`);
const headLink = (rel, href, hreflang = '') => {
  const link = document.createElement('link');
  link.rel = rel;
  link.href = href;
  if (hreflang) link.hreflang = hreflang;
  document.head.appendChild(link);
};
if (isIndexable && !document.querySelector('link[rel="canonical"]')) headLink('canonical', canonicalUrl);
if (isIndexable && !document.querySelector('link[rel="alternate"][hreflang="en"]')) {
  headLink('alternate', siteIsItalian ? `${canonicalOrigin}${alternatePath}` : canonicalUrl, 'en');
  headLink('alternate', siteIsItalian ? canonicalUrl : `${canonicalOrigin}${alternatePath}`, 'it');
  headLink('alternate', siteIsItalian ? `${canonicalOrigin}${alternatePath}` : canonicalUrl, 'x-default');
}
const pageDescription = document.querySelector('meta[name="description"]')?.content;
const socialMeta = [
  ['property', 'og:type', 'website'],
  ['property', 'og:title', document.title],
  ['property', 'og:url', canonicalUrl],
  ['property', 'og:locale', siteIsItalian ? 'it_IT' : 'en_GB'],
  ['name', 'twitter:card', 'summary']
];
if (pageDescription) socialMeta.push(['property', 'og:description', pageDescription], ['name', 'twitter:description', pageDescription]);
if (isIndexable) socialMeta.forEach(([attribute, key, content]) => {
  if (document.querySelector(`meta[${attribute}="${key}"]`)) return;
  const meta = document.createElement('meta');
  meta.setAttribute(attribute, key);
  meta.content = content;
  document.head.appendChild(meta);
});

const mainContent = document.querySelector('main');
if (mainContent && !mainContent.id) mainContent.id = 'main-content';
if (mainContent && !document.querySelector('.skip-link')) {
  const skipLink = document.createElement('a');
  skipLink.className = 'skip-link';
  skipLink.href = '#main-content';
  skipLink.textContent = siteIsItalian ? 'Vai al contenuto' : 'Skip to content';
  document.body.prepend(skipLink);
}

const siteHeader = document.querySelector('.site-header');
if (siteHeader && !siteHeader.querySelector('.sidebar-profile')) {
  const profile = document.createElement('div');
  profile.className = 'sidebar-profile';
  profile.innerHTML = `
    <a class="sidebar-portrait" href="index.html" aria-label="Caterina Mauri — home">
      <img src="${siteIsItalian ? '../' : ''}assets/caterina-mauri-senti-kiparla.jpg" alt="" width="152" height="152">
    </a>
    <p>${siteIsItalian ? 'Professoressa associata di Linguistica<br>Università di Bologna' : 'Associate Professor of Linguistics<br>University of Bologna'}</p>
  `;
  siteHeader.insertBefore(profile, siteHeader.querySelector('nav'));

  const contacts = document.createElement('div');
  contacts.className = 'sidebar-contacts';
  contacts.innerHTML = `
    <a href="mailto:caterina.mauri@unibo.it">caterina.mauri (at) unibo.it</a>
    <span><a href="https://orcid.org/0000-0002-8226-7846" target="_blank" rel="me noopener">ORCID ↗</a><a href="https://www.unibo.it/sitoweb/caterina.mauri/${siteIsItalian ? '' : 'en'}" target="_blank" rel="noopener">Unibo ↗</a></span>
  `;
  siteHeader.appendChild(contacts);
}

const currentFile = window.location.pathname.split('/').pop() || 'index.html';
if (['publications.html', 'talks.html', 'events.html'].includes(currentFile)) {
  const heroText = document.querySelector('.page-hero > p');
  if (heroText && !heroText.querySelector('.archive-context')) {
    const context = document.createElement('span');
    context.className = 'archive-context';
    context.textContent = siteIsItalian
      ? ' Le direzioni di ricerca nella home offrono selezioni tematiche trasversali a questo archivio completo.'
      : ' The research directions on the home page provide thematic selections across this complete archive.';
    heroText.appendChild(context);
  }
}
if (siteHeader && !siteHeader.querySelector('.language-switch')) {
  const languageSwitch = document.createElement('div');
  languageSwitch.className = 'language-switch';
  languageSwitch.setAttribute('aria-label', siteIsItalian ? 'Selezione lingua' : 'Language selection');
  languageSwitch.innerHTML = siteIsItalian
    ? `<a href="../${currentFile}">EN</a><span aria-current="true">IT</span>`
    : `<span aria-current="true">EN</span><a href="it/${currentFile}">IT</a>`;
  siteHeader.querySelector('.sidebar-profile')?.appendChild(languageSwitch);

  const mobileLanguageSwitch = languageSwitch.cloneNode(true);
  mobileLanguageSwitch.classList.add('mobile-language-switch');
  siteHeader.querySelector('.wordmark')?.insertAdjacentElement('afterend', mobileLanguageSwitch);
}
document.querySelectorAll('.site-header nav a').forEach((link) => {
  const linkFile = new URL(link.href, window.location.href).pathname.split('/').pop();
  if (linkFile === currentFile) link.setAttribute('aria-current', 'page');
  else link.removeAttribute('aria-current');
});
