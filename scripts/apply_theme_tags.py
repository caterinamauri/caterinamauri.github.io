#!/usr/bin/env python3
"""Apply reviewable thematic tags to the site's publications and talks."""

from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]

RULES = {
    "interaction": (
        r"interact|conversation|spoken|parlato|discourse|discours|co-?construction|"
        r"prosod|pragmatic|repair|common ground|response|dialog|turn[- ]taking|"
        r"joint production|incremental|listing|\blists?\b|esemplific|exemplif"
    ),
    "typology": (
        r"typolog|cross[- ]linguistic|linguistic diversity|diversità linguistica|"
        r"variation|variazione|world.?s languages|languages of (?:europe|the world)|"
        r"connective|coordination|conjunction|disjunction|modality|modalit|irrealis|"
        r"realis|grammaticali[sz]ation|grammaticalizzazione|diachron|change|mutamento|"
        r"relative clause|non-verbal predication|parts? of speech|language contact|"
        r"areal|standard and non-standard"
    ),
    "categories": (
        r"categor|meaning|semantic|significat|pragmatic|vagueness|vago|other|altro|"
        r"negation|negazione|response|common ground|knowledge|expectation|"
        r"connective|conjunction|disjunction|alternative|listing|\blists?\b|"
        r"esemplific|exemplif|reference|referenz"
    ),
    "data": (
        r"\bdata\b|\bdati\b|corpus|corpora|annotation|annotazione|resource|risors|"
        r"kiparla|parlabo|kipasti|stra-parla|treebank|universal dependencies|\bud\b|"
        r"method|metod|fieldwork|document|whisper|automatic speech|lrec|clarin|"
        r"repository|open science|multimodal"
    ),
}

OVERRIDES = {
    # Publications reviewed against abstracts/full texts.  These values describe
    # the four research directions on the home page, rather than surface words
    # occurring in titles or citations.
    "A diachronic view on non-verbal predication": ["interaction", "typology"],
    "Investigating ‘Other’ in Cross-Linguistic Perspective: Theoretical and Methodological Challenges": ["typology", "categories", "data"],
    "Shaping reference through temporality: the case of Italian nominals": ["typology", "categories"],
    "Temporal, aspectual, and modal evaluation in nominal reference: The case of Italian": ["typology", "categories"],
    "At the crossroads of typology and language(s) in use": ["interaction", "typology"],
    "‘Or’ cycles": ["interaction", "typology"],
    "The mirative values of Italian altro che": ["interaction", "categories"],
    "Multi-layered indexicality: When proper names become categories": ["interaction", "categories"],
    "Heterogeneous sets: a diachronic typology of associative and similative plurals": ["interaction", "typology"],
    "Ad hoc categorization in linguistic interaction": ["interaction", "categories"],
    "Building Categories in Interaction: Linguistic resources at work": ["interaction", "categories"],
    "Building categories in interaction. Theoretical and empirical perspectives": ["interaction", "categories"],
    "Esaustività e non esaustività esplicita nel discorso: dentro e oltre l'italiano": ["interaction", "typology", "categories"],
    "Diversità e inclusione. Quando le parole sono importanti": ["typology", "categories"],
    "Posizionamento del sé e rappresentazione dell’Altro nel discorso: una prospettiva interculturale": ["interaction", "categories"],
    "Senza e la connessione anticircostanziale: tra variazione tipologica e usi discorsivi": ["interaction", "typology"],
    "Introduzione": ["typology"],
    "La tipologia linguistica. Unità e diversità nelle lingue del mondo": ["typology"],
    "Le parti del discorso": ["typology"],
    "Exemplar-based compounds: The case of Chinese": ["typology", "categories"],
    "Questione di stile. L’espressione analitica della maniera indessicale": ["interaction", "categories"],
    "Why use or?": ["interaction", "typology", "categories"],
    "Uno, l’altro e un altro ancora: ambiguità dell’alterità tra sincronia e diacronia": ["interaction", "categories"],
    "Come districarsi tra descrizioni teoriche che offuscano i dati? Un approccio tipologico ai connettivi non-esaustivi oltre la logica": ["typology", "data"],
    "Special Issue: Linguistic strategies for the construction of ad hoc categories: synchronic and diachronic perspectives": ["interaction", "typology", "categories"],
    "Strategie linguistiche per la costruzione on-line di categorie: un quadro tipologico": ["interaction", "typology", "categories"],
    "Un approccio tipologico ai 'general extenders'": ["interaction", "typology"],
    "Building and interpreting ad hoc categories: a linguistic analysis": ["interaction", "categories"],
    "Come variano le lingue del mondo?": ["typology"],
    "Possiamo fare cose con le lingue?": ["interaction", "categories"],
    "Pathways to conditionality: two case studies from Italian": ["interaction", "typology"],
    "Tipologia Linguistica": ["typology"],
    "The reality status of directives and its coding across languages": ["typology", "categories"],
    "What do languages code when they code reality status?": ["typology", "categories"],
    "Go and come as sources of directive constructions": ["interaction", "typology"],
    "Synchrony and Diachrony. A dynamic interface.": ["interaction", "typology"],
    "Synchrony and Diachrony. Introduction to a dynamic interface": ["interaction", "typology"],
    "Cross-linguistic annotation of modality: a data-driven hierarchical model": ["typology", "data"],
    "Gradualness and pace in grammaticalization: The case of adversative connectives": ["interaction", "typology", "categories"],
    "The development of adversative connectives in Italian: stages and factors at play": ["interaction", "typology", "categories"],
    "How directive constructions emerge. Grammaticalization, constructionalization, cooptation": ["interaction", "typology"],
    "How directive constructions emerge: Grammaticalization, constructionalization, cooptation": ["interaction", "typology"],
    "The grammaticalization of coordinating interclausal connectives": ["interaction", "typology"],
    "I connettivi congiuntivi e avversativi dall'antico russo di Novgorod al russo moderno": ["interaction", "typology"],
    "I connettivi congiuntivi e avversativi dall’antico russo di Novgorod al russo moderno": ["interaction", "typology"],
    "Semantic Maps or Coding Maps? A unified account of the coding degree, coding distance and coding complexity of coordination relations.": ["typology", "data"],
    "Dalla continuità temporale al contrasto: la grammaticalizzazione di tuttavia come connettivo coordinativo": ["interaction", "typology"],
    "From cause to contrast. A study in semantic change": ["interaction", "typology"],
    "Mappe semantiche tra sincronia e diacronia: l'evoluzione delle strategie congiuntive e avversative nelle lingue slave": ["interaction", "typology", "data"],
    "recensione di M. Haspelmath (ed.), Coordinating Constructions, Amsterdam, Philadeplhia: John Benjamins (2004)": ["typology"],
    "Combinazione e contrasto: i connettivi congiuntivi e avversativi nelle lingue d’Europa": ["typology", "categories"],
    "Mettere in scena la comprensione: Dario Fo e la comunicazione oltre le parole": ["interaction", "categories"],
    "Oral and written needs: how literacy shapes the world’s grammars": ["interaction", "typology"],
    "Mirative rejection: When mistaken beliefs trigger surprise.": ["interaction", "categories"],
    "Esaustività e non-esaustività esplicita nel discorso: uno sguardo interlinguistico, tra funzioni testuali e percorsi diacronici’": ["interaction", "typology", "categories"],
    "Il posizionamento del sé nel discorso: una prospettiva interculturale.": ["interaction", "categories"],
    "Exemplar-based compounds: the case of Chinese.": ["typology", "categories"],
    "Questione di stile: l’espressione analitica della maniera indessicale.": ["interaction", "categories"],
    "Restricted indefiniteness: the case of Italian piuttosto che.": ["categories"],
    "Go and come as sources of directive constructions.": ["interaction", "typology"],
    "(with Andrea Sansò) ‘The reality status of directives and its coding across languages’": ["typology", "categories"],
    "(with Andrea Sansò) ‘The (ir)reality of directives”": ["typology", "categories"],
    "I connettivi congiuntivi e avversativi dall’antico russo di Novgorod al russo moderno.": ["typology", "categories"],
    "The reality status of directives and its coding across languages.": ["typology", "categories"],
    "Le relazioni di coordinazione: costruzioni congiuntive, disgiuntive e avversative a confronto": ["typology", "categories"],
    "Costruzioni congiuntive, disgiuntive e avversative nelle lingue d’Europa.": ["typology", "categories"],
}


def themes_for(item):
    title = item.get("title", "")
    if title in OVERRIDES:
        return OVERRIDES[title]
    text = " ".join(str(item.get(field, "")) for field in ("title", "citation", "event", "container_title"))
    inferred = [theme for theme, pattern in RULES.items() if re.search(pattern, text, re.I)]
    return inferred


def update(path, collection):
    payload = json.loads(path.read_text(encoding="utf-8"))
    items = payload[collection]
    for item in items:
        item["themes"] = themes_for(item)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    counts = {theme: sum(theme in item["themes"] for item in items) for theme in RULES}
    untagged = [item["title"] for item in items if not item["themes"]]
    print(f"{path.name}: {len(items)} records; {counts}; {len(untagged)} untagged")
    for title in untagged:
        print(f"  REVIEW: {title}")


if __name__ == "__main__":
    update(ROOT / "data" / "publications.json", "publications")
    update(ROOT / "data" / "talks.json", "talks")
