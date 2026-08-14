document.documentElement.lang = 'en';
document.querySelectorAll('[data-current-year]').forEach((element) => { element.textContent = new Date().getFullYear(); });

const siteHeader = document.querySelector('.site-header');
if (siteHeader && !siteHeader.querySelector('.sidebar-profile')) {
  const profile = document.createElement('div');
  profile.className = 'sidebar-profile';
  profile.innerHTML = `
    <a class="sidebar-portrait" href="index.html" aria-label="Caterina Mauri — home">
      <img src="assets/caterina-mauri-unibo.jpg" alt="" width="112" height="112">
    </a>
    <p>Associate Professor of Linguistics<br>University of Bologna</p>
  `;
  siteHeader.insertBefore(profile, siteHeader.querySelector('nav'));

  const contacts = document.createElement('div');
  contacts.className = 'sidebar-contacts';
  contacts.innerHTML = `
    <a href="mailto:caterina.mauri@unibo.it">caterina.mauri (at) unibo.it</a>
    <span><a href="https://orcid.org/0000-0002-8226-7846" target="_blank" rel="me noopener">ORCID ↗</a><a href="https://www.unibo.it/sitoweb/caterina.mauri/en" target="_blank" rel="noopener">Unibo ↗</a></span>
  `;
  siteHeader.appendChild(contacts);
}

const currentFile = window.location.pathname.split('/').pop() || 'index.html';
document.querySelectorAll('.site-header nav a').forEach((link) => {
  const linkFile = new URL(link.href, window.location.href).pathname.split('/').pop();
  if (linkFile === currentFile) link.setAttribute('aria-current', 'page');
  else link.removeAttribute('aria-current');
});
