"""
Surfaces recent arXiv papers that might be relevant to this loop's signal
research. Google Scholar has no API and blocks automated scraping; arXiv is
the free, ToS-compliant substitute, and it's where most quant/ML trading
research actually gets posted first anyway.

Safety boundary (same as idea_generator.py): this module only ever produces
human-readable leads (title, abstract snippet, link) for a human to read and
decide whether to act on. It NEVER turns a paper into a new signal
automatically -- that still requires a human to write a new evaluator
function in backtest_engine.py.
"""

import xml.etree.ElementTree as ET

import requests

ARXIV_API_URL = "http://export.arxiv.org/api/query"
ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}

KEYWORDS = [
    "liquidation",
    "order flow",
    "market microstructure",
    "orderbook imbalance",
    "momentum cryptocurrency",
    "mean reversion cryptocurrency",
    "high frequency trading signal",
    "cointegration pairs trading",
]
CATEGORIES = ["q-fin.TR", "q-fin.ST", "q-fin.CP"]
MAX_RESULTS = 5


def _build_query() -> str:
    cat_clause = " OR ".join(f"cat:{c}" for c in CATEGORIES)
    kw_clause = " OR ".join(f'all:"{k}"' for k in KEYWORDS)
    return f"({cat_clause}) AND ({kw_clause})"


def fetch_candidate_papers():
    """Returns a list of dicts: {arxiv_id, title, summary, link, published}.
    Returns [] on any network/parse error -- a research-scouting hiccup must
    never fail the research cycle itself."""
    params = {
        "search_query": _build_query(),
        "sortBy": "submittedDate",
        "sortOrder": "descending",
        "max_results": MAX_RESULTS,
    }
    try:
        resp = requests.get(ARXIV_API_URL, params=params, timeout=20)
        resp.raise_for_status()
        root = ET.fromstring(resp.text)
    except (requests.RequestException, ET.ParseError):
        return []

    papers = []
    for entry in root.findall("atom:entry", ATOM_NS):
        id_el = entry.find("atom:id", ATOM_NS)
        title_el = entry.find("atom:title", ATOM_NS)
        if id_el is None or title_el is None:
            continue
        summary_el = entry.find("atom:summary", ATOM_NS)
        published_el = entry.find("atom:published", ATOM_NS)
        link = id_el.text.strip()
        papers.append({
            "arxiv_id": link.rstrip("/").split("/abs/")[-1],
            "title": " ".join(title_el.text.split()),
            "summary": " ".join((summary_el.text or "").split())[:400] if summary_el is not None else "",
            "link": link,
            "published": published_el.text if published_el is not None else "",
        })
    return papers
