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

CHAPTER_METADATA_OVERRIDES = {
    "10.1515/9783110730982-002": {
        "editors": ["Pier Marco Bertinetto", "Luca Ciucci", "Denis Creissels"],
        "container_title": "Non-verbal Predication in the World’s Languages: A Typological Survey. Volume 1: Eurasia, North America, South America",
        "publisher": "De Gruyter Mouton",
        "publisher_place": "Berlin and Boston",
        "pages": "57-86",
    },
    "10.1163/9789004744196_009": {
        "editors": ["Patrícia Amaral"],
        "container_title": "Other: Ambiguity, Constraints, and Change",
    },
}

OFFICIAL_LINK_OVERRIDES = {
    "Coconstructions in Spoken Data: UD Annotation Guidelines and First Results": "https://doi.org/10.63317/3kcohrckgnkz",
    "Say again? The limits of Whisper with conversation: A case study on the KIParla corpus": "https://doi.org/10.63317/2so5y449gb4w",
    "Introducing KIParla Forest: seeds for a UD annotation of interactional syntax.": "https://aclanthology.org/2025.depling-1.5/",
    "Did Somebody Say 'Gest-IT'? A Pilot Exploration of Multimodal Data Management": "https://ceur-ws.org/Vol-3878/80_main_long.pdf",
    "KIParla corpus: A new resource for spoken Italian": "https://aclanthology.org/2019.clicit-1.37/",
    "Building and interpreting ad hoc categories: a linguistic analysis": "https://doi.org/10.1007/978-3-319-48832-5_16",
    "Go and come as sources of directive constructions": "https://doi.org/10.1515/9783110335989.165",
    "Coordination": "https://doi.org/10.5040/9781472542090.ch-017",
    "Connectives": "https://doi.org/10.1017/CBO9781139022453.021",
    "The grammaticalization of coordinating interclausal connectives": "https://doi.org/10.1093/oxfordhb/9780199586783.013.0054",
    "Coordination Relations in the Languages of Europe and Beyond": "https://doi.org/10.1515/9783110211498",
    "From cause to contrast. A study in semantic change": "https://doi.org/10.1515/9783110211764.4.303",
    "Conjunctive, disjunctive and adversative constructions in Europe: some areal considerations": "https://doi.org/10.1075/slcs.88.10mau",
    "Dubitative corrective constructions in Italian: their use and rise in discourse": "https://doi.org/10.1075/slcs.186.13ram",
    "Synchrony and Diachrony. A dynamic interface.": "https://doi.org/10.1075/slcs.133",
    "Synchrony and Diachrony. Introduction to a dynamic interface": "https://doi.org/10.1075/slcs.133.01int",
    "Ad hoc categorization and language: the construction of categories in discourse": "https://www.sciencedirect.com/journal/language-sciences/special-issues",
    "CATEGORIZATION AS AN AD HOC PROCESS IN DISCOURSE": "https://www.cambridgescholars.com/resources/pdfs/978-1-5275-8908-7-sample.pdf",
    "Diversità e inclusione. Quando le parole sono importanti": "https://www.meltemieditore.it/catalogo/diversita-e-inclusione/",
    "Posizionamento del sé e rappresentazione dell’Altro nel discorso: una prospettiva interculturale": "https://www.meltemieditore.it/catalogo/diversita-e-inclusione/",
    "Italiano parlato e variazione linguistica. Teoria e prassi nella costruzione del corpus KIParla": "https://www.patroneditore.com/volumi/9788855535724/italiano-parlato-e-variazione-linguistica",
    "La tipologia linguistica. Unità e diversità nelle lingue del mondo": "https://www.carocci.it/prodotto/la-tipologia-linguistica",
    "Introduzione": "https://www.carocci.it/prodotto/la-tipologia-linguistica",
    "Le parti del discorso": "https://www.carocci.it/prodotto/la-tipologia-linguistica",
    "Obiettivi, metodi e strumenti della tipologia": "https://www.carocci.it/prodotto/la-tipologia-linguistica",
    "La diversità linguistica": "https://www.carocci.it/prodotto/la-diversita-linguistica",
    "Come variano le lingue del mondo?": "https://www.caissa.it/299-tutto-cio-che-hai-sempre-voluto-sapere-sul-linguaggio-e-sulle-lingue-9788867290444.html",
    "Possiamo fare cose con le lingue?": "https://www.caissa.it/299-tutto-cio-che-hai-sempre-voluto-sapere-sul-linguaggio-e-sulle-lingue-9788867290444.html",
    "Un approccio tipologico ai 'general extenders'": "https://www.francoangeli.it/Libro/9788891778475/Tipologia%2C-Acquisizione%2C-Grammaticalizzazione.-Typology%2C-Acquisition%2C-Grammaticalization-Studies?id=25216",
    "Lists: description, delimitation, definition. A foreword": "https://doi.org/10.26346/1120-2726-115",
    "Cross-linguistic annotation of modality: a data-driven hierarchical model": "https://aclanthology.org/W13-0501/",
    "The added value of the Connectivity Hypothesis for the map of parts of speech. Comment on ‘An implicational map of parts of speech’ by Kees Hengeveld and Eva van Lier (2010)": "https://doi.org/10.1349/PS1.1537-0852.A.370",
    "Pathways to conditionality: two case studies from Italian": "https://doi.org/10.1400/236607",
    "LES ÉTUDES TYPOLOGIQUES EN ITALIE": "https://doi.org/10.15122/isbn.978-2-406-05686-7.p.0073",
}


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
                    "pages": extract_pages(citation),
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


def extract_pages(citation):
    """Recover page ranges that Unibo exposes only inside the full citation."""
    match = re.search(
        r"\bpp?\.\s*(?P<pages>(?:\d+|[IVXLCDM]+)(?:\s*[-–]\s*(?:\d+|[IVXLCDM]+))?)",
        citation,
        re.IGNORECASE,
    )
    if not match:
        return ""
    return re.sub(r"\s*[-–]\s*", "-", match.group("pages"))


def english_iris_url(url):
    """Ask the IRIS/DSpace interface for English when it remains the fallback."""
    if "cris.unibo.it/handle/" not in url or "locale-attribute=" in url:
        return url
    separator = "&" if "?" in url else "?"
    return f"{url}{separator}locale-attribute=en"


def apply_official_link_policy(item):
    """Expose publisher links publicly; retain no CRIS fallback on the website."""
    override = OFFICIAL_LINK_OVERRIDES.get(item.get("title", ""))
    if override:
        item["url"] = override
        item["link_type"] = "doi" if "doi.org/" in override else "official_publication"
    elif "cris.unibo.it" in item.get("url", ""):
        item["url"] = ""
        item["link_type"] = "citation_only"
    return item


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
            enrich_chapter_metadata(item, doi)
        elif item["open_access"] and pdf_url:
            item["url"] = pdf_url
            item["link_type"] = "open_access_pdf"
    except Exception as error:
        print(f"Keeping IRIS fallback for {item['url']}: {error}")
    return item


def enrich_chapter_metadata(item, doi=None):
    """Add volume editors and container metadata from DOI CSL for book chapters."""
    if item.get("type") != "chapters":
        return item
    doi = doi or (item.get("url", "").removeprefix("https://doi.org/") if "doi.org/" in item.get("url", "") else "")
    if not doi:
        return item
    override = CHAPTER_METADATA_OVERRIDES.get(doi.lower())
    if override:
        item.update(override)
    try:
        request = urllib.request.Request(
            f"https://doi.org/{doi}",
            headers={
                "Accept": "application/vnd.citationstyles.csl+json",
                "User-Agent": "CaterinaMauriWebsite/1.0",
            },
        )
        with urllib.request.urlopen(request, timeout=20, context=SSL_CONTEXT) as response:
            metadata = json.loads(response.read().decode("utf-8"))
        editors = []
        for person in metadata.get("editor", []):
            full_name = clean(" ".join(part for part in (person.get("given", ""), person.get("family", "")) if part))
            if full_name:
                editors.append(full_name)
        container = metadata.get("container-title", "")
        if isinstance(container, list):
            container = container[0] if container else ""
        item["editors"] = editors
        item["container_title"] = clean(re.sub(r"<[^>]+>", "", container))
        item["publisher"] = clean(metadata.get("publisher", ""))
        item["publisher_place"] = clean(metadata.get("publisher-place", ""))
        item["pages"] = clean(metadata.get("page", ""))
        if override:
            item.update(override)
    except Exception as error:
        print(f"Could not enrich chapter metadata for {doi}: {error}")
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


def write_archives(publications, preserve_resources=False):
    for item in publications:
        if not item.get("pages"):
            item["pages"] = extract_pages(item.get("citation", ""))
        apply_official_link_policy(item)

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
    if not preserve_resources:
        RESOURCES_OUTPUT.write_text(json.dumps(resources_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Saved {len(scholarly_publications)} publications to {OUTPUT}")
    if not preserve_resources:
        print(f"Saved {len(resources)} resources to {RESOURCES_OUTPUT}")


def main():
    arguments = argparse.ArgumentParser()
    arguments.add_argument("--from-cache", action="store_true", help="Split the existing synchronized archive without fetching Unibo")
    arguments.add_argument("--normalize-links", action="store_true", help="Apply the public-link policy to the cached archive")
    options = arguments.parse_args()

    if options.normalize_links:
        publications = json.loads(OUTPUT.read_text(encoding="utf-8"))["publications"]
    elif options.from_cache:
        publications = json.loads(OUTPUT.read_text(encoding="utf-8"))["publications"]
        with ThreadPoolExecutor(max_workers=6) as executor:
            publications = list(executor.map(enrich_chapter_metadata, publications))
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

    write_archives(publications, preserve_resources=options.from_cache or options.normalize_links)


if __name__ == "__main__":
    main()
