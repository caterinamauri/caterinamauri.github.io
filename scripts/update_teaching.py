#!/usr/bin/env python3
"""Build the current teaching list from Caterina Mauri's Unibo profile."""

from html import unescape
from pathlib import Path
import json
import re
import urllib.request

URL = "https://www.unibo.it/sitoweb/caterina.mauri/didattica"
OUTPUT = Path(__file__).resolve().parents[1] / "data" / "teaching.json"


def clean(value):
    value = re.sub(r"<br\s*/?>", " · ", value, flags=re.I)
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", unescape(value)).strip(" ·")


def main():
    request = urllib.request.Request(URL, headers={"User-Agent": "CaterinaMauriWebsite/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        html = response.read().decode("utf-8")

    blocks = re.findall(r'<div class="linked-data-list">(.*?)</div>\s*</div>', html, re.S)
    courses = []
    for block in blocks:
        heading = re.search(r'<h4>\s*<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', block, re.S)
        if not heading:
            continue
        title = clean(heading.group(2))
        degree = re.search(r'<th>Corso:</th>\s*<td>\s*<p>(.*?)</p>', block, re.S)
        period = re.search(r'<p>(Periodo delle lezioni:.*?)</p>', block, re.S)
        courses.append({
            "title": re.sub(r"^[A-Z0-9]+\s*-\s*", "", title),
            "url": heading.group(1),
            "degree": clean(degree.group(1)) if degree else "",
            "period": clean(period.group(1)) if period else "",
        })

    if not courses:
        raise RuntimeError("No courses found; keeping the existing archive is safer.")
    year = re.search(r'Insegnamenti\s+(\d{4}-\d{4})', html)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps({"source": URL, "academic_year": year.group(1) if year else "", "courses": courses}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Saved {len(courses)} courses to {OUTPUT}")


if __name__ == "__main__":
    main()
