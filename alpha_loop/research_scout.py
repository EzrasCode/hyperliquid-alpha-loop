"""
Surfaces candidate research leads from four free, ToS-compliant sources.
Google Scholar has no API and blocks scraping; X/Twitter search now requires
a paid tier -- both excluded on those grounds (see
docs/research/alpha_loop/alpha_loop_overview_20260927.md).

Safety boundary (same as idea_generator.py): every function here only ever
produces human-readable leads (title, snippet, link) for a human to read and
decide whether to act on. Nothing is auto-converted into a running signal --
that still requires a human to write a new evaluator function in
backtest_engine.py.

Each source function returns a list of dicts with a common shape:
{source, external_id, title, summary, link, published} -- `published` is an
ISO date string (best-effort; some sources don't give one). Every function
degrades to [] on any network/parse error rather than raising, since a
research-scouting hiccup must never fail the research cycle itself.
"""

import xml.etree.ElementTree as ET
from datetime import datetime, timezone

import requests

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
MAX_RESULTS_PER_SOURCE = 5
REQUEST_TIMEOUT = 20


# ==================== arXiv ====================

ARXIV_API_URL = "http://export.arxiv.org/api/query"
ARXIV_ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}
ARXIV_CATEGORIES = ["q-fin.TR", "q-fin.ST", "q-fin.CP"]


def fetch_arxiv_papers():
    cat_clause = " OR ".join(f"cat:{c}" for c in ARXIV_CATEGORIES)
    kw_clause = " OR ".join(f'all:"{k}"' for k in KEYWORDS)
    params = {
        "search_query": f"({cat_clause}) AND ({kw_clause})",
        "sortBy": "submittedDate",
        "sortOrder": "descending",
        "max_results": MAX_RESULTS_PER_SOURCE,
    }
    try:
        resp = requests.get(ARXIV_API_URL, params=params, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        root = ET.fromstring(resp.text)
    except (requests.RequestException, ET.ParseError):
        return []

    papers = []
    for entry in root.findall("atom:entry", ARXIV_ATOM_NS):
        id_el = entry.find("atom:id", ARXIV_ATOM_NS)
        title_el = entry.find("atom:title", ARXIV_ATOM_NS)
        if id_el is None or title_el is None:
            continue
        summary_el = entry.find("atom:summary", ARXIV_ATOM_NS)
        published_el = entry.find("atom:published", ARXIV_ATOM_NS)
        link = id_el.text.strip()
        papers.append({
            "source": "arxiv",
            "external_id": link.rstrip("/").split("/abs/")[-1],
            "title": " ".join(title_el.text.split()),
            "summary": " ".join((summary_el.text or "").split())[:400] if summary_el is not None else "",
            "link": link,
            "published": published_el.text if published_el is not None else "",
        })
    return papers


# ==================== Semantic Scholar ====================

SEMANTIC_SCHOLAR_URL = "https://api.semanticscholar.org/graph/v1/paper/search"


def fetch_semantic_scholar_papers():
    import os

    query = " OR ".join(KEYWORDS[:4])  # API query strings get unreliable past a few OR terms
    params = {
        "query": query,
        "fields": "title,abstract,url,publicationDate,externalIds",
        "limit": MAX_RESULTS_PER_SOURCE,
    }
    # Free, no-cost API key raises the shared unauthenticated rate limit
    # substantially -- optional, same pattern as OPENROUTER_API_KEY.
    headers = {}
    api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
    if api_key:
        headers["x-api-key"] = api_key
    try:
        resp = requests.get(SEMANTIC_SCHOLAR_URL, params=params, headers=headers, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
    except (requests.RequestException, ValueError):
        return []

    papers = []
    for item in data.get("data", []):
        paper_id = item.get("paperId")
        if not paper_id or not item.get("title"):
            continue
        papers.append({
            "source": "semantic_scholar",
            "external_id": paper_id,
            "title": item["title"],
            "summary": (item.get("abstract") or "")[:400],
            "link": item.get("url") or f"https://www.semanticscholar.org/paper/{paper_id}",
            "published": item.get("publicationDate") or "",
        })
    return papers


# ==================== Quantocracy (curated quant-blog RSS) ====================

QUANTOCRACY_FEED_URL = "https://quantocracy.com/feed/"


QUANTOCRACY_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; alpha-loop-research-scout/1.0)"}


def fetch_quantocracy_posts():
    try:
        resp = requests.get(QUANTOCRACY_FEED_URL, headers=QUANTOCRACY_HEADERS, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        root = ET.fromstring(resp.content)
    except (requests.RequestException, ET.ParseError):
        return []

    posts = []
    for item in root.findall(".//item")[:MAX_RESULTS_PER_SOURCE]:
        title_el, link_el = item.find("title"), item.find("link")
        if title_el is None or link_el is None:
            continue
        desc_el, guid_el, date_el = item.find("description"), item.find("guid"), item.find("pubDate")
        posts.append({
            "source": "quantocracy",
            "external_id": (guid_el.text if guid_el is not None else link_el.text),
            "title": title_el.text or "",
            "summary": " ".join((desc_el.text or "").split())[:400] if desc_el is not None else "",
            "link": link_el.text,
            "published": date_el.text if date_el is not None else "",
        })
    return posts


# ==================== Reddit (r/algotrading + r/quant search) ====================

REDDIT_SEARCH_URL = "https://www.reddit.com/r/algotrading+quant/search.json"
REDDIT_HEADERS = {"User-Agent": "alpha-loop-research-scout/1.0"}


def fetch_reddit_posts():
    params = {
        "q": " OR ".join(KEYWORDS[:4]),
        "restrict_sr": 1,
        "sort": "top",
        "t": "week",
        "limit": MAX_RESULTS_PER_SOURCE,
    }
    try:
        resp = requests.get(REDDIT_SEARCH_URL, params=params, headers=REDDIT_HEADERS, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
    except (requests.RequestException, ValueError):
        return []

    posts = []
    for child in data.get("data", {}).get("children", []):
        p = child.get("data", {})
        if not p.get("id") or not p.get("title"):
            continue
        published = ""
        if p.get("created_utc"):
            published = datetime.fromtimestamp(p["created_utc"], tz=timezone.utc).isoformat()
        posts.append({
            "source": "reddit",
            "external_id": p["id"],
            "title": p["title"],
            "summary": (p.get("selftext") or "")[:400],
            "link": f"https://reddit.com{p.get('permalink', '')}",
            "published": published,
        })
    return posts


# ==================== GitHub (trending repos matching keywords) ====================

GITHUB_SEARCH_URL = "https://api.github.com/search/repositories"


def fetch_github_repos():
    params = {
        "q": "hyperliquid liquidation trading strategy in:name,description",
        "sort": "updated",
        "order": "desc",
        "per_page": MAX_RESULTS_PER_SOURCE,
    }
    try:
        resp = requests.get(GITHUB_SEARCH_URL, params=params, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
    except (requests.RequestException, ValueError):
        return []

    repos = []
    for item in data.get("items", []):
        if not item.get("id") or not item.get("full_name"):
            continue
        repos.append({
            "source": "github",
            "external_id": str(item["id"]),
            "title": item["full_name"],
            "summary": (item.get("description") or "")[:400],
            "link": item.get("html_url", ""),
            "published": item.get("updated_at") or "",
        })
    return repos


ALL_SOURCES = [fetch_arxiv_papers, fetch_semantic_scholar_papers, fetch_quantocracy_posts, fetch_github_repos]
# fetch_reddit_posts is defined but not active: Reddit locked down its public
# JSON endpoints in 2023 and now serves a bot-verification page to any
# unauthenticated script. It only works with real OAuth credentials from a
# registered Reddit API app -- add it back to ALL_SOURCES if that's ever set up.


def fetch_all_candidates():
    """Runs every source, tolerating individual failures, and returns one
    combined list in the common lead shape."""
    leads = []
    for fetch_fn in ALL_SOURCES:
        leads.extend(fetch_fn())
    return leads
