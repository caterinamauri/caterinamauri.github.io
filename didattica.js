const teachingIsItalian = document.documentElement.lang === 'it';
const teachingScriptUrl = document.querySelector('script[src*="didattica.js"]')?.src || window.location.href;
const teachingDataUrl = new URL('data/teaching.json', teachingScriptUrl);
const teachingItalianLabels = new Map([
  ['Linguistic Diversity (MA) — 6 ECTS', 'Diversità linguistica (LM) — 6 CFU'],
  ['General Linguistics — 9 ECTS', 'Linguistica generale — 9 CFU'],
  ['Pragmatics (MA) — 6 ECTS', 'Pragmatica (LM) — 6 CFU'],
  ['Semantics and Pragmatics — 9 ECTS', 'Semantica e pragmatica — 9 CFU'],
  ['Teaching L2 Italian, Plurilingualism, Interculturality', 'Didattica dell’italiano L2, plurilinguismo e interculturalità'],
  ['Italian Culture and Language for Foreigners', 'Lingua e cultura italiane per stranieri'],
  ['Languages, Markets and Cultures of Asia and Mediterranean Africa', 'Lingue, mercati e culture dell’Asia e dell’Africa mediterranea'],
  ['Data, Methods and Theoretical Models for Linguistics', 'Dati, metodi e modelli teorici per la linguistica'],
  ['Semiotics', 'Semiotica'],
  ['Foreign Languages and Literature', 'Lingue e letterature straniere']
]);
function teachingLabel(value) { return teachingIsItalian ? (teachingItalianLabels.get(value) || value) : value; }
function teachingPeriod(value) {
  if (!teachingIsItalian || !value) return value;
  return value.replace('Teaching period:', 'Periodo delle lezioni:').replace('September', 'settembre').replace('November', 'novembre').replace('December', 'dicembre');
}

fetch(teachingDataUrl, { cache: 'no-store' })
  .then((response) => { if (!response.ok) throw new Error(`HTTP ${response.status}`); return response; })
  .then((response) => response.json())
  .then((data) => {
    const years = data.years || {[data.academic_year]: data.courses};
    const yearNames = Object.keys(years).sort().reverse();
    const tabs = document.querySelector('#teaching-years');
    const courseList = document.querySelector('#current-courses');
    const renderCourses = (year) => {
      courseList.innerHTML = years[year].map((course) => {
        const programmeLinks = course.programmes?.length
          ? `<div class="programme-links"><span>${teachingIsItalian ? 'Offerto nei corsi di studio' : 'Offered in'}</span>${course.programmes.map((programme) => `<a href="${programme.url}" target="_blank" rel="noopener">${teachingLabel(programme.title)} ↗</a>`).join('')}</div>`
          : '';
        const period = course.period ? `<p class="course-period">${teachingPeriod(course.period)}</p>` : '';
        return `<article><div><h3><a href="${course.url}" target="_blank" rel="noopener">${teachingLabel(course.title)}</a></h3>${programmeLinks}${period}</div></article>`;
      }).join('');
      tabs.querySelectorAll('button').forEach((button) => button.setAttribute('aria-selected', button.dataset.year === year ? 'true' : 'false'));
    };
    tabs.innerHTML = yearNames.map((year, index) => `<button type="button" data-year="${year}" aria-selected="${index === 0}">${teachingIsItalian ? 'A.A.' : 'A.Y.'} ${year.replace('-', '/')}</button>`).join('') + `<a href="cv.html">${teachingIsItalian ? 'Per gli anni precedenti: CV completo' : 'Earlier years: see Full CV'} ↗</a>`;
    tabs.addEventListener('click', (event) => {
      const button = event.target.closest('button[data-year]');
      if (button) renderCourses(button.dataset.year);
    });
    renderCourses(data.current_year || yearNames[0]);
  })
  .catch(() => {
    document.querySelector('#current-courses').innerHTML = `<p>${teachingIsItalian ? 'Gli insegnamenti sono temporaneamente disponibili sul profilo Unibo.' : 'Current courses are temporarily available on the Unibo profile.'}</p>`;
  });
