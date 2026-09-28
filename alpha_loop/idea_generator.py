"""
Proposes new hypothesis *parameterizations* via a single OpenRouter call.

Safety boundary (see hypothesis_bank.py docstring): the model only ever picks
a `kind` from KNOWN_KINDS plus numeric/string params matching
KIND_PARAM_SCHEMA. Its output is JSON, parsed and validated -- never eval()d
or exec()d. If it proposes a kind we don't recognize, or params that don't
validate, that item is dropped, not retried into something looser.
"""

import json
import os

from dotenv import load_dotenv

from . import config
from .hypothesis_bank import Hypothesis, KIND_PARAM_SCHEMA, KNOWN_KINDS

load_dotenv()

SYSTEM_PROMPT = """You are a quantitative researcher proposing NEW parameterizations \
of existing signal templates for a Hyperliquid alpha-mining loop. You do NOT write code. \
You output ONLY a JSON array, nothing else -- no prose, no markdown fences.

Each item must be:
{"name": "<short description>", "kind": "<one of the allowed kinds>", "coin": "<BTC|ETH|SOL|XRP|HYPE>", "params": {...}}

Allowed kinds and their params:
%s

Propose parameterizations that are plausibly different from what's likely already \
been tried (vary thresholds, coins, or timeframes) rather than near-duplicates. \
Return at most %d items.""" % (
    json.dumps(KIND_PARAM_SCHEMA, indent=2),
    config.IDEA_GEN_MAX_NEW_PER_CALL,
)


def _client():
    from openai import OpenAI

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return None
    return OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")


def _validate_item(item) -> Hypothesis | None:
    if not isinstance(item, dict):
        return None
    kind = item.get("kind")
    coin = item.get("coin")
    params = item.get("params")
    name = item.get("name") or f"generated {kind}"
    if kind not in KNOWN_KINDS or not isinstance(coin, str) or not isinstance(params, dict):
        return None
    expected_keys = set(KIND_PARAM_SCHEMA[kind].keys())
    if not expected_keys.issubset(params.keys()):
        return None
    for key, value in params.items():
        if key in ("timeframe", "tick_duration") and not isinstance(value, str):
            return None
        if key not in ("timeframe", "tick_duration") and not isinstance(value, (int, float)):
            return None
    return Hypothesis(name=name, kind=kind, coin=coin.upper(), params=params, source="generated")


def propose_new_hypotheses(recent_context: str) -> list[Hypothesis]:
    """Returns a validated list of new Hypothesis objects (possibly empty)."""
    client = _client()
    if client is None:
        return []

    prompt = (
        "Recent backtest context (hypothesis name -> n samples, hit_rate, mean_return):\n"
        f"{recent_context}\n\n"
        "Propose new parameterizations to try next."
    )

    try:
        response = client.chat.completions.create(
            model=config.IDEA_GEN_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            max_tokens=1024,
            temperature=0.9,
        )
        content = response.choices[0].message.content.strip()
    except Exception:
        return []

    content = content.strip("` \n")
    if content.lower().startswith("json"):
        content = content[4:].strip()

    try:
        items = json.loads(content)
    except (json.JSONDecodeError, TypeError):
        return []

    if not isinstance(items, list):
        return []

    hypotheses = []
    for item in items[: config.IDEA_GEN_MAX_NEW_PER_CALL]:
        h = _validate_item(item)
        if h is not None:
            hypotheses.append(h)
    return hypotheses
