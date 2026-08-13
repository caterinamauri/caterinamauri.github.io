document.documentElement.lang = 'en';
document.querySelectorAll('[data-current-year]').forEach((element) => { element.textContent = new Date().getFullYear(); });

const currentFile = window.location.pathname.split('/').pop() || 'index.html';
document.querySelectorAll('.site-header nav a').forEach((link) => {
  const linkFile = new URL(link.href, window.location.href).pathname.split('/').pop();
  if (linkFile === currentFile) link.setAttribute('aria-current', 'page');
  else link.removeAttribute('aria-current');
});
