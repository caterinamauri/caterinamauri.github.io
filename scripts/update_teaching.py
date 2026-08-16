#!/usr/bin/env python3
"""Build the current teaching list from Caterina Mauri's Unibo profile."""

from html import unescape
from pathlib import Path
import json
import re
import urllib.request

URL = "https://www.unibo.it/sitoweb/caterina.mauri/didattica"
OUTPUT = Path(__file__).resolve().parents[1] / "data" / "teaching.json"

PROGRAMMES = {
    "Laurea Magistrale in Didattica dell'italiano L2, plurilinguismo, interculturalità": ("Teaching L2 Italian, Plurilingualism, Interculturality", "https://corsi.unibo.it/2cycle/ItalianL2PlurilingualismInterculturality"),
    "Laurea Magistrale in Lingua e cultura italiane per stranieri": ("Italian Culture and Language for Foreigners", "https://corsi.unibo.it/2cycle/ItalianCulture"),
    "Laurea in Lingue, mercati e culture dell'Asia e dell'Africa mediterranea": ("Languages, Markets and Cultures of Asia and Mediterranean Africa", "https://corsi.unibo.it/1cycle/AsianLanguagesMarketsCultures"),
    "Laurea Magistrale in Dati, metodi e modelli per le scienze linguistiche": ("Data, Methods and Theoretical Models for Linguistics", "https://corsi.unibo.it/2cycle/DataMethodsTheoreticalModelsLinguistics"),
    "Laurea Magistrale in Semiotica": ("Semiotics", "https://corsi.unibo.it/2cycle/Semiotics"),
}

COURSE_TITLES = {
    "DIVERSITA' LINGUISTICA (LM) - 6 cfu": "Linguistic Diversity (MA) — 6 ECTS",
    "LINGUISTICA GENERALE - 9 cfu": "General Linguistics — 9 ECTS",
    "PRAGMATICA (1) (LM) - 6 cfu": "Pragmatics (MA) — 6 ECTS",
}

MONTHS = {
    "gennaio": "January", "febbraio": "February", "marzo": "March",
    "aprile": "April", "maggio": "May", "giugno": "June",
    "luglio": "July", "agosto": "August", "settembre": "September",
    "ottobre": "October", "novembre": "November", "dicembre": "December",
}


def translate_period(value):
    match = re.fullmatch(r"Periodo delle lezioni: dal (\d+) (\w+) (\d{4}) al (\d+) (\w+) (\d{4})", value)
    if not match:
        return value
    start_day, start_month, start_year, end_day, end_month, end_year = match.groups()
    start_year_text = f" {start_year}" if start_year != end_year else ""
    return f"Teaching period: {start_day} {MONTHS.get(start_month, start_month)}{start_year_text}–{end_day} {MONTHS.get(end_month, end_month)} {end_year}"


def clean(value):
    value = re.sub(r"<br\s*/?>", " · ", value, flags=re.I)
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", unescape(value)).strip(" ·")


def main():
    request = urllib.request.Request(URL, headers={"User-Agent": "CaterinaMauriWebsite/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        html = response.read().decode("utf-8")

    blocks = re.findall(r'<div class="linked-data-list">(.*?)</div>\s*</div>', html, re.S)
    year = re.search(r'Insegnamenti\s+(\d{4})-\d{4}', html)
    catalogue_year = year.group(1) if year else ""
    courses = []
    for block in blocks:
        heading = re.search(r'<h4>\s*<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', block, re.S)
        if not heading:
            continue
        title = clean(heading.group(2))
        course_url = heading.group(1)
        course_id = re.search(r"/(\d{4})/(\d+)/?$", course_url)
        if course_id:
            course_url = f"https://www.unibo.it/en/study/course-units-transferable-skills-moocs/course-unit-catalogue/course-unit/{course_id.group(1)}/{course_id.group(2)}"
        degree = re.search(r'<th>Corso:</th>\s*<td>\s*<p>(.*?)</p>', block, re.S)
        period = re.search(r'<p>(Periodo delle lezioni:.*?)</p>', block, re.S)
        degree_text = clean(degree.group(1)) if degree else ""
        programmes = []
        for degree_name in (part.strip() for part in degree_text.split(" · ")):
            if degree_name in PROGRAMMES:
                programme_title, programme_url = PROGRAMMES[degree_name]
                programmes.append({
                    "title": programme_title,
                    "url": programme_url,
                })
        courses.append({
            "title": COURSE_TITLES.get(re.sub(r"^[A-Z0-9]+\s*-\s*", "", title), re.sub(r"^[A-Z0-9]+\s*-\s*", "", title)),
            "url": course_url,
            "degree": degree_text,
            "programmes": programmes,
            "period": translate_period(clean(period.group(1))) if period else "",
        })

    if not courses:
        raise RuntimeError("No courses found; keeping the existing archive is safer.")
    academic_year = re.search(r'Insegnamenti\s+(\d{4}-\d{4})', html)
    current_year = academic_year.group(1) if academic_year else ""
    archive = json.loads(OUTPUT.read_text(encoding="utf-8")) if OUTPUT.exists() else {}
    years = archive.get("years", {})
    years[current_year] = courses
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps({"source": URL, "current_year": current_year, "years": years}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Saved {len(courses)} courses to {OUTPUT}")


if __name__ == "__main__":
    main()
