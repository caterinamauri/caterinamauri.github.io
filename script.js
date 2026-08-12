const switcher = document.querySelector('.lang-switch');
const translatable = document.querySelectorAll('[data-en][data-it]');

function setLanguage(language) {
  document.documentElement.lang = language;
  translatable.forEach((element) => {
    element.textContent = element.dataset[language];
  });
  switcher.textContent = language === 'en' ? 'IT' : 'EN';
  switcher.setAttribute('aria-label', language === 'en' ? "Passa all'italiano" : 'Switch to English');
  localStorage.setItem('cm-language', language);
}

switcher.addEventListener('click', () => {
  setLanguage(document.documentElement.lang === 'en' ? 'it' : 'en');
});

setLanguage(localStorage.getItem('cm-language') || 'en');
document.querySelector('#year').textContent = new Date().getFullYear();

const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.12 });

document.querySelectorAll('.reveal').forEach((element) => observer.observe(element));
