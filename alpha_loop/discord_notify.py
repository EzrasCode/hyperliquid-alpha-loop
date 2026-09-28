"""
Posts each cycle's summary to a Discord webhook. No-ops if
DISCORD_WEBHOOK_URL isn't set, so local/dev runs don't require one, and never
raises -- a Discord hiccup must never fail the research cycle itself.
"""

import os

import requests
from dotenv import load_dotenv

load_dotenv()

MAX_DESCRIPTION_LEN = 3800  # Discord embed description hard limit is 4096
EMBED_COLOR = 0x9B59B6


def send_cycle_summary(cycle: int, summary: str):
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        return

    body = summary if len(summary) <= MAX_DESCRIPTION_LEN else summary[:MAX_DESCRIPTION_LEN] + "\n... (truncated)"
    payload = {
        "username": "Alpha Loop",
        "embeds": [
            {
                "title": f"\U0001f319 Alpha Loop -- cycle {cycle}",
                "description": f"```\n{body}\n```",
                "color": EMBED_COLOR,
            }
        ],
    }
    try:
        requests.post(webhook_url, json=payload, timeout=15)
    except requests.RequestException:
        pass


def send_research_leads(papers: list):
    """papers: list of dicts from research_scout.fetch_candidate_papers()."""
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url or not papers:
        return

    blocks = []
    for p in papers:
        snippet = p["summary"][:220] + ("..." if len(p["summary"]) > 220 else "")
        blocks.append(f"**{p['title']}**\n{snippet}\n{p['link']}")
    description = "\n\n".join(blocks)
    if len(description) > MAX_DESCRIPTION_LEN:
        description = description[:MAX_DESCRIPTION_LEN] + "\n... (truncated)"
    description += "\n\n_Not yet converted to a testable signal -- needs manual review._"

    payload = {
        "username": "Alpha Loop",
        "embeds": [
            {
                "title": f"\U0001f4da New research lead(s) -- {len(papers)} paper(s)",
                "description": description,
                "color": 0x3498DB,
            }
        ],
    }
    try:
        requests.post(webhook_url, json=payload, timeout=15)
    except requests.RequestException:
        pass
