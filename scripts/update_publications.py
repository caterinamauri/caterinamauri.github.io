#!/usr/bin/env python3
"""Build the site's publication archive from Caterina Mauri's Unibo profile."""

from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import argparse
import json
import re
import ssl
import urllib.request

try:
    import certifi
    SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    SSL_CONTEXT = ssl.create_default_context()

BASE_URL = "https://www.unibo.it/sitoweb/caterina.mauri/publications"
OUTPUT = Path(__file__).resolve().parents[1] / "data" / "publications.json"
RESOURCES_OUTPUT = Path(__file__).resolve().parents[1] / "data" / "resources.json"


class PublicationParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.items = []
        self.current = None
        self.in_author = False
        self.in_title = False

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "p" and self.current is None:
            self.current = {"text": [], "authors": [], "title": [], "url": "", "open_access": False}
        if not self.current:
            return
        if tag == "span" and "author" in attributes.get("class", "").split():
            self.in_author = True
        if tag == "span" and "label-openaccess" in attributes.get("class", "").split():
            self.current["open_access"] = True
        if tag == "a" and self.in_title:
            self.current["url"] = attributes.get("href", "")
        if tag == "em":
            self.in_title = True

    def handle_endtag(self, tag):
        if not self.current:
            return
        if tag == "span":
            self.in_author = False
        elif tag == "em":
            self.in_title = False
        elif tag == "p":
            title = clean("".join(self.current["title"]))
            authors = clean("".join(self.current["authors"]))
            citation = clean("".join(self.current["text"]))
            if title and authors and "cris.unibo.it" in self.current["url"]:
                year_match = re.search(r"\b(19|20)\d{2}\b", citation)
                self.items.append({
                    "title": title,
                    "authors": authors,
                    "year": int(year_match.group()) if year_match else None,
                    "citation": citation,
                    "url": english_iris_url(self.current["url"]),
                    "open_access": self.current["open_access"],
                    "type": publication_type(citation),
                    "link_type": "iris",
                })
            self.current = None

    def handle_data(self, data):
        if not self.current:
            return
        self.current["text"].append(data)
        if self.in_author:
            self.current["authors"].append(data)
        if self.in_title:
            self.current["title"].append(data)


def clean(value):
    return re.sub(r"\s+", " ", unescape(value)).strip()


def english_iris_url(url):
    """Ask the IRIS/DSpace interface for English when it remains the fallback."""
    if "cris.unibo.it/handle/" not in url or "locale-attribute=" in url:
        return url
    separator = "&" if "?" in url else "?"
    return f"{url}{separator}locale-attribute=en"


class ItemMetadataParser(HTMLParser):
    """Read standard scholarly metadata exposed by an IRIS item page."""

    def __init__(self):
        super().__init__()
        self.metadata = {}

    def handle_starttag(self, tag, attrs):
        if tag != "meta":
            return
        attributes = dict(attrs)
        name = attributes.get("name", "").lower()
        if name in {"citation_doi", "citation_pdf_url"}:
            self.metadata[name] = attributes.get("content", "").strip()


def enrich_link(item):
    """Prefer a DOI, then an open-access PDF, keeping IRIS as a safe fallback."""
    try:
        request = urllib.request.Request(item["url"], headers={"User-Agent": "CaterinaMauriWebsite/1.0"})
        with urllib.request.urlopen(request, timeout=20, context=SSL_CONTEXT) as response:
            parser = ItemMetadataParser()
            parser.feed(response.read().decode("utf-8", errors="replace"))
        doi = parser.metadata.get("citation_doi")
        pdf_url = parser.metadata.get("citation_pdf_url")
        if doi:
            item["url"] = f"https://doi.org/{doi}"
            item["link_type"] = "doi"
        elif item["open_access"] and pdf_url:
            item["url"] = pdf_url
            item["link_type"] = "open_access_pdf"
    except Exception as error:
        print(f"Keeping IRIS fallback for {item['url']}: {error}")
    return item


def publication_type(citation):
    match = re.search(r"\[([^\]]+)\]\s*(?:Open Access)?$", citation, re.IGNORECASE)
    raw = match.group(1).lower() if match else ""
    if any(label in raw for label in ("curatela", "editorship")):
        return "edited"
    if any(label in raw for label in ("articolo", "article")):
        return "articles"
    if any(word in raw for word in ("capitolo", "introduzione", "prefazione", "chapter", "essay", "introduction")):
        return "chapters"
    if any(word in raw for word in ("atti", "contributo", "conference proceedings")):
        return "proceedings"
    if any(word in raw for word in ("banc", "dataset", "database")):
        return "resources"
    if any(word in raw for word in ("libro", "monografia", "book", "monograph")):
        return "books"
    return "other"


def fetch_page(page):
    url = BASE_URL if page == 1 else f"{BASE_URL}?page={page}"
    request = urllib.request.Request(url, headers={"User-Agent": "CaterinaMauriWebsite/1.0"})
    with urllib.request.urlopen(request, timeout=30, context=SSL_CONTEXT) as response:
        return response.read().decode("utf-8")


def write_archives(publications):
    iris_resources = [item for item in publications if item["type"] == "resources"]
    scholarly_publications = [item for item in publications if item["type"] != "resources"]

    # KIParla Forest is an official external resource but is not currently
    # represented in IRIS with its Universal Dependencies access point.
    supplements = [{
        "title": "KIParla Forest",
        "authors": "Pannitto, Ludovica; Zucchini, Eleonora; Bosco, Cristina; Mauri, Caterina; Sanguinetti, Manuela; Cocco, Esther",
        "year": 2025,
        "citation": "A Universal Dependencies treebank of spoken Italian in interaction, based on KIParla.",
        "url": "https://universaldependencies.org/treebanks/it_kiparlaforest/index.html",
        "open_access": True,
        "type": "resources",
        "link_type": "official_resource",
        "source": "Universal Dependencies",
        "link_label": "Open resource ↗",
    }, {
        "title": "Gest-IT",
        "authors": "Pannitto, Ludovica; Albanesi, Lorenzo; Marion, Laura; Martines, Federica Maria; Caruso, Carmelo; Bianchini, Claudia S.; Masini, Francesca; Mauri, Caterina",
        "year": 2024,
        "citation": "A pilot multimodal corpus combining orthographic, prosodic and gestural annotation of conversations involving sighted people and people with visual impairment.",
        "url": "https://ceur-ws.org/Vol-3878/80_main_long.pdf",
        "open_access": True,
        "type": "resources",
        "link_type": "related_publication",
        "source": "Gest-IT / CLiC-it 2024",
        "link_label": "Read project paper ↗",
    }]
    resources = list(iris_resources)
    for supplement in supplements:
        matching_iris = next(
            (item for item in resources if item.get("title", "").casefold().startswith(supplement["title"].casefold())),
            None,
        )
        if matching_iris:
            matching_iris["secondary_url"] = supplement["url"]
            matching_iris["secondary_link_label"] = "Universal Dependencies ↗"
            matching_iris["secondary_source"] = supplement["source"]
        else:
            resources.append(supplement)
    resources.sort(key=lambda item: (item.get("year") or 0, item.get("title", "")), reverse=True)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "source": BASE_URL,
        "count": len(scholarly_publications),
        "publications": scholarly_publications,
    }
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    resources_payload = {
        "source": BASE_URL,
        "count": len(resources),
        "resources": resources,
    }
    RESOURCES_OUTPUT.write_text(json.dumps(resources_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Saved {len(scholarly_publications)} publications to {OUTPUT}")
    print(f"Saved {len(resources)} resources to {RESOURCES_OUTPUT}")


def main():
    arguments = argparse.ArgumentParser()
    arguments.add_argument("--from-cache", action="store_true", help="Split the existing synchronized archive without fetching Unibo")
    options = arguments.parse_args()

    if options.from_cache:
        publications = json.loads(OUTPUT.read_text(encoding="utf-8"))["publications"]
    else:
        publications = []
        seen = set()
        for page in range(1, 21):
            parser = PublicationParser()
            parser.feed(fetch_page(page))
            fresh = [item for item in parser.items if item["url"] not in seen]
            if not fresh:
                break
            publications.extend(fresh)
            seen.update(item["url"] for item in fresh)

        if not publications:
            raise RuntimeError("No publications found; keeping the existing archive is safer.")

        with ThreadPoolExecutor(max_workers=6) as executor:
            publications = list(executor.map(enrich_link, publications))

    write_archives(publications)


if __name__ == "__main__":
    main()
