#!/usr/bin/env python3
"""Create the two canonical CV files from CURRICULUM VITAE.docx."""

from copy import deepcopy
from datetime import datetime
from pathlib import Path
import json
import re
import shutil
import tempfile
import zipfile
import xml.etree.ElementTree as ET

from docx import Document
from docx.oxml.ns import qn


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
SOURCE = ASSETS / "CURRICULUM VITAE.docx"
MAIN = ASSETS / "Mauri_CV.docx"
FULL = ASSETS / "Mauri_CV_tutto.docx"
XLSX_PRIMARY = Path("/Users/caterinamauri/Downloads/elenco1.xlsx")
XLSX_SECONDARY = Path("/Users/caterinamauri/Downloads/elenco2.xlsx")
RESOURCES = ROOT / "data" / "resources.json"

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}
ET.register_namespace("w", W)


def q(name):
    return f"{{{W}}}{name}"


def ptext(p):
    return "".join(t.text or "" for t in p.findall(".//w:t", NS))


def first_rpr(p):
    for r in p.findall(".//w:r", NS):
        if "".join(t.text or "" for t in r.findall(".//w:t", NS)).strip():
            rpr = r.find("w:rPr", NS)
            return deepcopy(rpr) if rpr is not None else None
    return None


def make_run(text, rpr=None, bold=False):
    r = ET.Element(q("r"))
    rp = deepcopy(rpr) if rpr is not None else ET.Element(q("rPr"))
    for b in list(rp.findall("w:b", NS)):
        rp.remove(b)
    if bold:
        ET.SubElement(rp, q("b"))
    r.append(rp)
    t = ET.SubElement(r, q("t"))
    if text.startswith(" ") or text.endswith(" "):
        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    t.text = text
    return r


def set_runs(p, pieces):
    rpr = first_rpr(p)
    for child in list(p):
        if child.tag != q("pPr"):
            p.remove(child)
    for text, bold in pieces:
        p.append(make_run(text, rpr, bold))


TOKEN = re.compile(
    r"\((?:(?:19|20)\d{2}[a-z]?(?:\s*,\s*[^)]*)?|accepted(?:\s*,\s*in press)?|"
    r"submitted|in preparation(?:\s*,\s*under contract)?|in press)\)", re.I
)


def normalize_first_author(authors):
    authors = re.sub(r"\s+", " ", authors).strip(" ,.;")
    sep = ";" if ";" in authors else ("," if re.match(r"^(?:Caterina|Silvia|Nicola|Alessandra|Cristina)\b", authors) else None)
    if ";" in authors:
        first, rest = authors.split(";", 1)
        joiner = "; "
    else:
        first, rest, joiner = authors, "", ""
    first = first.strip(" ,")
    explicit = {
        "Caterina, Mauri": "Mauri, Caterina",
        "Caterina Mauri": "Mauri, Caterina",
        "Silvia Ballarè": "Ballarè, Silvia",
        "Nicola Grandi": "Grandi, Nicola",
        "Alessandra Barotto": "Barotto, Alessandra",
        "Cristina Bosco": "Bosco, Cristina",
        "Arcodia Giorgio Francesco": "Arcodia, Giorgio Francesco",
        "Da Milano Federica": "Da Milano, Federica",
        "Giacalone Ramat A.": "Giacalone Ramat, A.",
        "Giacalone Ramat Anna": "Giacalone Ramat, Anna",
        "Arcodia G.F.": "Arcodia, G.F.",
        "Nissim M.": "Nissim, M.",
    }
    first = explicit.get(first, first)
    if "," not in first:
        parts = first.split()
        if len(parts) >= 2:
            # Only deterministic given-name-first forms occurring in this CV.
            if parts[0] in {"Caterina", "Silvia", "Nicola", "Alessandra", "Cristina"}:
                first = f"{' '.join(parts[1:])}, {parts[0]}"
    return first + (joiner + rest.strip() if rest.strip() else "")


def format_publication(text):
    number = ""
    mnum = re.match(r"\s*(\d+\.\s*)", text)
    if mnum:
        number, text = mnum.group(1), text[mnum.end():]
    mt = TOKEN.search(text)
    if not mt:
        raise ValueError(f"No year/status token: {text[:100]}")
    authors = normalize_first_author(text[:mt.start()])
    remainder = text[mt.end():].strip()
    remainder = re.sub(r"^[.,;:]\s*", "", remainder)
    # Keep the original bibliographic content, changing only its prefix/order.
    if remainder.lower().startswith("with "):
        # Legacy fallback entries: author data was omitted; Caterina is first.
        authors = "Mauri, Caterina"
    suffix = f"{authors}. {remainder}" if remainder else authors
    return number, mt.group(0), suffix


def resource_records():
    data = json.loads(RESOURCES.read_text(encoding="utf-8"))["resources"]
    by_key = {re.sub(r"[^a-z0-9]+", "", r["title"].lower()): r for r in data}
    return by_key


def format_resources(paragraphs):
    records = resource_records()
    for p in paragraphs:
        text = ptext(p)
        low = text.lower()
        if "kipos" in low:
            year = "2020"
            authors = "Bosco, Cristina; Ballarè, Silvia; Cerruti, Massimo; Goria, Eugenio; Mauri, Caterina"
            rest = "KIPoS: KIParla Part-of-Speech tagging resource. http://www.di.unito.it/~tutreeb/kipos-evalita2020/index.html"
        else:
            match = None
            for record in records.values():
                title_words = re.sub(r"^corpus\s+", "", record["title"].lower()).split()
                if title_words and title_words[0] in low:
                    match = record
                    break
            if "kiparla forest" in low:
                match = next(r for r in records.values() if "forest" in r["title"].lower())
            elif "stra-parlabo" in low:
                match = next(r for r in records.values() if "stra-parlabo" in r["title"].lower())
            elif "kipasti" in low:
                match = next(r for r in records.values() if "kipasti" in r["title"].lower())
            elif "parlabo" in low and "stra-" not in low:
                match = next(r for r in records.values() if r["title"].lower() == "corpus parlabo")
            elif re.search(r"\bkip corpus\b", low):
                match = next(r for r in records.values() if r["title"].lower() == "corpus kip")
            elif "co-coordinator of corpus kiparla" in low:
                match = next(r for r in records.values() if r["title"].lower() == "corpus kiparla")
            if match is None:
                raise ValueError(f"No resource metadata for: {text}")
            year = str(match["year"])
            authors = match["authors"]
            # Expand initials where the local record contains only initials.
            if "forest" in match["title"].lower():
                authors = "Pannitto, Ludovica; Zucchini, Eleonora; Ballarè, Silvia; Bosco, Cristina; Mauri, Caterina; Sanguinetti, Manuela"
            rest = f"{match['title']}. {match['url']}"
            if match.get("secondary_url"):
                rest += f" {match['secondary_url']}"
        set_runs(p, [(f"({year})", True), (f" {authors}. {rest}", False)])


def reorder_cv(source, output):
    with zipfile.ZipFile(source) as zin:
        root = ET.fromstring(zin.read("word/document.xml"))
        paragraphs = root.findall(".//w:body/w:p", NS)
        texts = [ptext(p).strip() for p in paragraphs]
        pub_heading = texts.index("10. Publications")
        res_heading = texts.index("Linguistic resources")
        talks_heading = next(i for i, t in enumerate(texts) if t.startswith("11. Invited talks"))
        pub_count = 0
        for p in paragraphs[pub_heading + 1:res_heading]:
            text = ptext(p).strip()
            if not text or text in {"Monographs", "Edited volumes and special issues", "Articles in peer-reviewed journals", "Papers and chapters within edited volumes"}:
                continue
            number, token, suffix = format_publication(text)
            set_runs(p, [(number, False), (token, True), (f" {suffix}", False)])
            pub_count += 1
        resource_ps = [p for p in paragraphs[res_heading + 1:talks_heading] if ptext(p).strip()]
        format_resources(resource_ps)
        xml = ET.tostring(root, encoding="utf-8", xml_declaration=True)
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False, dir=output.parent) as tmp:
            tmp_path = Path(tmp.name)
        with zipfile.ZipFile(tmp_path, "w") as zout:
            for item in zin.infolist():
                zout.writestr(item, xml if item.filename == "word/document.xml" else zin.read(item.filename))
        tmp_path.replace(output)
    return pub_count, len(resource_ps)


def xlsx_rows(path):
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    with zipfile.ZipFile(path) as z:
        shared = []
        if "xl/sharedStrings.xml" in z.namelist():
            sroot = ET.fromstring(z.read("xl/sharedStrings.xml"))
            shared = ["".join(t.text or "" for t in si.findall(".//m:t", ns)) for si in sroot.findall("m:si", ns)]
        root = ET.fromstring(z.read("xl/worksheets/sheet1.xml"))
        for row in root.findall(".//m:sheetData/m:row", ns):
            values = {}
            for c in row.findall("m:c", ns):
                col = re.match(r"[A-Z]+", c.get("r")).group()
                typ = c.get("t")
                v = c.find("m:v", ns)
                val = "" if v is None else (v.text or "")
                if typ == "s" and val:
                    val = shared[int(val)]
                elif typ == "inlineStr":
                    val = "".join(t.text or "" for t in c.findall(".//m:t", ns))
                values[col] = re.sub(r"\s+", " ", val).strip()
            if values.get("G") and values.get("M") and re.search(r"(?:19|20)\d{2}", values["M"]):
                yield {
                    "title": values["G"],
                    "year": re.search(r"(?:19|20)\d{2}", values["M"]).group(),
                    "degree": values.get("I", ""),
                }


def thesis_rows(path):
    seen = set()
    rows = []
    for row in xlsx_rows(path):
        key = (row["title"].casefold(), row["year"], row["degree"].casefold())
        if key not in seen:
            seen.add(key)
            rows.append(row)
    return sorted(rows, key=lambda x: (-int(x["year"]), x["title"].casefold()))


def pavia_rows():
    course = "LINGUISTICA TEORICA, APPLICATA E DELLE LINGUE MODERNE [05409]"
    values = [
        ("Categorizzare con liste ed esempi: uno studio condotto attraverso l'eye tracking", "2014/2015"),
        ("I connettivi ipotetico-presupposizionali dell'italiano contemporaneo: definizione e proposta di analisi", "2012/2013"),
        ("Il netspeak dei fandom - un'analisi linguistica", "2014/2015"),
        ("Le funzioni dei complimenti", "2012/2013"),
        ("Le funzioni dell'esemplificazione in italiano: tra cognizione e discorso", "2014/2015"),
        ("Strutture comparative a base nominale: graduabilità e categorie cognitive", "2015/2016"),
        ("Un corpus per segnare: corpus linguistics nella didattica e nell'apprendimento della lingua dei segni", "2011/2012"),
        ("Dentro la barzelletta: moderni approcci linguistico-cognitivi allo studio di storielle divertenti", "2015/2016"),
        ("Il code switching: variazione di codice in madrelingua cinesi residenti in Italia", "2014/2015"),
    ]
    return [{"title": title, "year": year, "degree": course} for title, year in values]


def append_theses(source, output):
    primary = thesis_rows(XLSX_PRIMARY)
    secondary = thesis_rows(XLSX_SECONDARY)
    pavia = pavia_rows()
    with zipfile.ZipFile(source) as zin:
        root = ET.fromstring(zin.read("word/document.xml"))
        body = root.find(".//w:body", NS)
        paragraphs = body.findall("w:p", NS)
        anchor = next(p for p in paragraphs if ptext(p).strip().startswith("11. Invited talks"))
        template = next(p for p in paragraphs if "Corpus KIParla" in ptext(p))
        anchor_rpr = first_rpr(anchor)
        set_runs(anchor, [("12. Invited talks and lectures", False)])

        def insert_paragraph(text, bold=False, heading=False):
            clone = deepcopy(anchor if heading else template)
            set_runs(clone, [(text, bold)])
            body.insert(list(body).index(anchor), clone)

        insert_paragraph("11. Supervised BA and MA theses", heading=True)
        insert_paragraph("University of Bologna — Primary supervisor", bold=True)
        for row in primary:
            insert_paragraph(f"{row['title']} ({row['year']}). {row['degree']}")
        insert_paragraph("University of Pavia — Primary supervisor", bold=True)
        for row in sorted(pavia, key=lambda x: (x["year"], x["title"].casefold()), reverse=True):
            insert_paragraph(f"{row['title']} ({row['year']}). {row['degree']}")
        insert_paragraph("University of Bologna — Co-supervisor", bold=True)
        for row in secondary:
            insert_paragraph(f"{row['title']} ({row['year']}). {row['degree']}")

        xml = ET.tostring(root, encoding="utf-8", xml_declaration=True)
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False, dir=output.parent) as tmp:
            tmp_path = Path(tmp.name)
        with zipfile.ZipFile(tmp_path, "w") as zout:
            for item in zin.infolist():
                zout.writestr(item, xml if item.filename == "word/document.xml" else zin.read(item.filename))
        tmp_path.replace(output)
    return len(primary), len(secondary), len(pavia)


def structural_check(path, expected_publications, expected_resources, thesis_counts=None):
    with zipfile.ZipFile(path) as z:
        bad = z.testzip()
        if bad:
            raise RuntimeError(f"Corrupt ZIP member: {bad}")
        root = ET.fromstring(z.read("word/document.xml"))
    paragraphs = root.findall(".//w:body/w:p", NS)
    texts = [ptext(p).strip() for p in paragraphs]
    pub = texts.index("10. Publications")
    res = texts.index("Linguistic resources")
    talks = next(i for i, t in enumerate(texts) if "Invited talks and lectures" in t)
    publication_ps = [p for p in paragraphs[pub + 1:res] if ptext(p).strip() and ptext(p).strip() not in {"Monographs", "Edited volumes and special issues", "Articles in peer-reviewed journals", "Papers and chapters within edited volumes"}]
    resource_ps = [p for p in paragraphs[res + 1:talks] if ptext(p).strip()]
    if thesis_counts:
        th = texts.index("11. Supervised BA and MA theses")
        resource_ps = [p for p in paragraphs[res + 1:th] if ptext(p).strip()]
    assert len(publication_ps) == expected_publications
    assert len(resource_ps) == expected_resources
    for p in publication_ps + resource_ps:
        text = ptext(p).strip()
        assert re.match(r"(?:\d+\.\s*)?\(", text), text
        first_text_run = next((r for r in p.findall("w:r", NS) if ptext(r).strip().startswith("(")), None)
        if first_text_run is None:  # numbered monograph: token is the second run
            first_text_run = next(r for r in p.findall("w:r", NS) if "(" in ptext(r))
        assert first_text_run.find("w:rPr/w:b", NS) is not None, text
    full_text = "\n".join(texts)
    assert "@studio.unibo.it" not in full_text
    if thesis_counts:
        assert "11. Supervised BA and MA theses" in texts
        assert "12. Invited talks and lectures" in texts
    return len(publication_ps), len(resource_ps)


def main():
    if not SOURCE.exists():
        raise SystemExit(f"Missing source: {SOURCE}")
    pub_count, resource_count = reorder_cv(SOURCE, MAIN)
    primary_count, secondary_count, pavia_count = append_theses(MAIN, FULL)
    structural_check(MAIN, pub_count, resource_count)
    structural_check(FULL, pub_count, resource_count, (primary_count, secondary_count))
    print(f"Created {MAIN.name}: {pub_count} publications, {resource_count} resources")
    print(f"Created {FULL.name}: +{primary_count} Bologna primary, +{pavia_count} Pavia primary, and +{secondary_count} Bologna co-supervisor theses")


if __name__ == "__main__":
    main()
