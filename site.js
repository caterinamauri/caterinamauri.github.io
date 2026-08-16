const siteIsItalian = document.documentElement.lang === 'it';
document.querySelectorAll('[data-current-year]').forEach((element) => { element.textContent = new Date().getFullYear(); });

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
document.querySelectorAll('.site-header nav').forEach((nav) => {
  if (!nav.querySelector('a[href="talks.html"]')) {
    const talksLink = document.createElement('a');
    talksLink.href = 'talks.html';
    talksLink.textContent = siteIsItalian ? 'Interventi' : 'Talks';
    const publicationsLink = nav.querySelector('a[href="publications.html"]');
    if (publicationsLink) publicationsLink.insertAdjacentElement('afterend', talksLink);
    else nav.appendChild(talksLink);
  }
});

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
