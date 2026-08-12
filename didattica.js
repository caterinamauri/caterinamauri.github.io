document.documentElement.lang = 'en';
document.querySelector('#year').textContent = new Date().getFullYear();

fetch('data/teaching.json')
  .then((response) => response.json())
  .then((data) => {
    document.querySelector('#academic-year').textContent = `A.A. ${data.academic_year}`;
    document.querySelector('#current-courses').innerHTML = data.courses.map((course) => `
      <article><time>${data.academic_year}</time><div><h3><a href="${course.url}" target="_blank" rel="noopener">${course.title}</a></h3><p>${course.degree}</p><p class="course-period">${course.period}</p></div></article>`).join('');
  })
  .catch(() => {
    document.querySelector('#current-courses').innerHTML = '<p>Current courses are temporarily available on the Unibo profile.</p>';
  });
