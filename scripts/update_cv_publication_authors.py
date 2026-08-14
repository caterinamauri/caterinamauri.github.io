#!/usr/bin/env python3
"""Replace CV publication prefixes with explicit authors and a bold year/status."""

from copy import deepcopy
from difflib import SequenceMatcher
import json
from pathlib import Path
import re
import tempfile
import unicodedata
import zipfile
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "Caterina-Mauri-CV.docx"
OUTPUT = ROOT / "assets" / "Caterina-Mauri-CV-updated.docx"
PUBLICATIONS = ROOT / "data" / "publications.json"

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}
ET.register_namespace("w", W)


def qn(name):
    return f"{{{W}}}{name}"


def normalize(value):
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def paragraph_text(paragraph):
    return "".join(node.text or "" for node in paragraph.findall(".//w:t", NS))


def quoted_title(text):
    pairs = [("“", "”"), ('"', '"'), ("‘", "’")]
    candidates = []
    for opening, closing in pairs:
        start = text.find(opening)
        if start < 0:
            continue
        end = text.rfind(closing)
        if end > start:
            candidates.append((start, text[start + 1:end]))
    return min(candidates, default=(None, ""), key=lambda item: item[0] if item[0] is not None else 10**9)


def year_token(text):
    match = re.search(r"\((?:19|20)\d{2}[a-z]?[^)]*\)|\((?:accepted|submitted|in preparation)[^)]*\)", text, re.I)
    return match.group(0) if match else "(year unavailable)"


def clean_authors(value):
    value = value.replace("*", "")
    value = re.sub(r"\bCaterina\s+Mauri\b", "Mauri, Caterina", value, flags=re.I)
    value = re.sub(r"\bMauri\s+Caterina\b", "Mauri, Caterina", value, flags=re.I)
    value = re.sub(r"\bMauri,?\s+C\.?\b", "Mauri, Caterina", value, flags=re.I)
    return re.sub(r"\s+", " ", value).strip()


def likely_item(text, items):
    token = year_token(text)
    year_match = re.search(r"(?:19|20)\d{2}", token)
    year = int(year_match.group()) if year_match else None
    title_start, title = quoted_title(text)
    eligible = [item for item in items if year is None or item.get("year") in (None, year)]

    if title:
        title_norm = normalize(title)
        ranked = sorted(
            ((SequenceMatcher(None, title_norm, normalize(item["title"])).ratio(), item) for item in eligible),
            key=lambda pair: pair[0],
            reverse=True,
        )
        if ranked and ranked[0][0] >= 0.86:
            return ranked[0][1], title_start
        return None, title_start

    folded = text.casefold()
    exact = []
    for item in eligible:
        title_value = item["title"]
        position = folded.find(title_value.casefold())
        if position >= 0:
            exact.append((len(title_value), position, item))
    if exact:
        _, position, item = max(exact)
        return item, position

    token_match = re.search(re.escape(token), text, re.I)
    remainder_start = token_match.end() if token_match else 0
    remainder = text[remainder_start:]
    with_match = re.match(r"\s*,?\s*with\b.*?[.,]\s+", remainder, re.I)
    if with_match:
        remainder_start += with_match.end()
    else:
        remainder_start += len(remainder) - len(remainder.lstrip(" ,.;\u00a0"))
    return None, remainder_start


def source_run_properties(paragraph):
    for run in paragraph.findall(".//w:r", NS):
        if any((node.text or "").strip() for node in run.findall(".//w:t", NS)):
            properties = run.find("w:rPr", NS)
            return deepcopy(properties) if properties is not None else None
    return None


def new_run(text, properties=None, bold=False):
    run = ET.Element(qn("r"))
    run_properties = deepcopy(properties) if properties is not None else ET.Element(qn("rPr"))
    if bold and run_properties.find("w:b", NS) is None:
        run_properties.append(ET.Element(qn("b")))
    run.append(run_properties)
    text_node = ET.SubElement(run, qn("t"))
    if text.startswith(" ") or text.endswith(" "):
        text_node.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    text_node.text = text
    return run


def replace_prefix(paragraph, cut_at, authors, token):
    properties = source_run_properties(paragraph)
    text_nodes = paragraph.findall(".//w:t", NS)
    offset = 0
    insertion_child = None
    for child in list(paragraph):
        child_nodes = child.findall(".//w:t", NS)
        child_start = offset
        child_length = sum(len(node.text or "") for node in child_nodes)
        if insertion_child is None and child_start + child_length > cut_at:
            insertion_child = child
        offset += child_length

    offset = 0
    for node in text_nodes:
        value = node.text or ""
        end = offset + len(value)
        if end <= cut_at:
            node.text = ""
        elif offset < cut_at:
            node.text = value[cut_at - offset:]
        offset = end

    number_match = re.match(r"\s*(\d+\.\s*)", paragraph_text_before_edit)
    number = number_match.group(1) if number_match else ""
    insertion_index = list(paragraph).index(insertion_child) if insertion_child is not None else len(paragraph)
    prefix_runs = [
        new_run(f"{number}{authors} ", properties),
        new_run(token, properties, bold=True),
        new_run(". ", properties),
    ]
    for run in reversed(prefix_runs):
        paragraph.insert(insertion_index, run)


def main():
    items = json.loads(PUBLICATIONS.read_text(encoding="utf-8"))["publications"]
    with zipfile.ZipFile(SOURCE) as archive:
        document_xml = archive.read("word/document.xml")
        root = ET.fromstring(document_xml)
        paragraphs = root.findall(".//w:body/w:p", NS)

        ranges = list(range(75, 78)) + list(range(81, 93)) + list(range(96, 146)) + list(range(150, 200))
        report = []
        global paragraph_text_before_edit
        for index in ranges:
            paragraph = paragraphs[index]
            paragraph_text_before_edit = paragraph_text(paragraph)
            if not paragraph_text_before_edit.strip():
                continue
            item, title_start = likely_item(paragraph_text_before_edit, items)
            authors = clean_authors(item.get("authors", "")) if item else "Mauri, Caterina"
            if not authors:
                authors = "Mauri, Caterina"
            token = year_token(paragraph_text_before_edit)
            replace_prefix(paragraph, title_start, authors, token)
            report.append({
                "paragraph": index,
                "matched": bool(item),
                "title": item["title"] if item else "",
                "authors": authors,
                "token": token,
            })

        updated_xml = ET.tostring(root, encoding="utf-8", xml_declaration=True)
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False, dir=OUTPUT.parent) as temporary:
            temporary_path = Path(temporary.name)
        with zipfile.ZipFile(temporary_path, "w") as output_archive:
            for entry in archive.infolist():
                content = updated_xml if entry.filename == "word/document.xml" else archive.read(entry.filename)
                output_archive.writestr(entry, content)
        temporary_path.replace(OUTPUT)

    report_path = ROOT / "output" / "cv-publication-author-report.json"
    report_path.parent.mkdir(exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Updated {len(report)} publication entries: {OUTPUT}")
    print(f"Matched {sum(row['matched'] for row in report)} entries; fallback used for {sum(not row['matched'] for row in report)}")


if __name__ == "__main__":
    main()
