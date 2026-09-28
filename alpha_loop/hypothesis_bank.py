"""
Structured, declarative hypothesis specs for the alpha-mining loop.

Every hypothesis is one of a small whitelist of evaluator "kinds" (see
backtest_engine.KIND_EVALUATORS). idea_generator.py can only ever emit new
*parameterizations* of these kinds -- new thresholds, coins, or confidence
levels -- never arbitrary code. This is a deliberate safety boundary: the
loop never eval()s or exec()s anything an LLM produces. Adding a genuinely
new signal kind requires a human to write a new evaluator function in
backtest_engine.py and register it in KIND_EVALUATORS.

See docs/research/alpha_loop/alpha_loop_overview_20260927.md for why these
five were chosen.
"""

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Dict

HORIZONS_MINUTES = {"5m": 5, "15m": 15, "1h": 60, "4h": 240}

KNOWN_KINDS = {
    "hlp_sentiment_threshold",
    "liq_momentum",
    "smart_money_top",
    "cvd_divergence",
    "cross_exchange_liq_leadlag",
}


@dataclass
class Hypothesis:
    name: str
    kind: str
    coin: str
    params: Dict[str, Any] = field(default_factory=dict)
    source: str = "seed"  # "seed" | "generated"

    @property
    def spec_hash(self) -> str:
        payload = json.dumps(
            {"kind": self.kind, "coin": self.coin, "params": self.params},
            sort_keys=True,
        )
        return hashlib.sha256(payload.encode()).hexdigest()[:16]

    @property
    def id(self) -> str:
        return f"{self.kind}__{self.coin}__{self.spec_hash}"


SEED_HYPOTHESES = [
    Hypothesis(
        name="HLP sentiment squeeze (z >= 2.0)",
        kind="hlp_sentiment_threshold",
        coin="BTC",
        params={"z_threshold": 2.0},
    ),
    Hypothesis(
        name="HLP sentiment squeeze (z >= 2.5, extreme)",
        kind="hlp_sentiment_threshold",
        coin="BTC",
        params={"z_threshold": 2.5},
    ),
    Hypothesis(
        name="Liquidation cascade momentum (5m concentration)",
        kind="liq_momentum",
        coin="BTC",
        params={"min_5m_usd": 500_000.0, "concentration_ratio": 0.5},
    ),
    Hypothesis(
        name="Smart money top signal (confidence >= 0.6, 1h)",
        kind="smart_money_top",
        coin="BTC",  # actual traded coin comes from the fired signal itself
        params={"timeframe": "1h", "min_confidence": 0.6},
    ),
    Hypothesis(
        name="CVD / price divergence (BTC, 1h ticks)",
        kind="cvd_divergence",
        coin="BTC",
        params={
            "tick_duration": "1h",
            "min_abs_price_change_pct": 0.02,
            "min_abs_cvd": 10,
        },
    ),
    Hypothesis(
        name="Cross-exchange liquidation lead-lag (Binance -> HL)",
        kind="cross_exchange_liq_leadlag",
        coin="BTC",
        params={
            "timeframe": "10m",
            "min_binance_usd": 1_000_000.0,
            "lead_ratio": 2.0,
        },
    ),
]

# Documents each kind's expected params for idea_generator.py's prompt and
# for validating LLM-proposed parameterizations before they're stored.
def extract_trigger_fields(hypothesis: "Hypothesis", raw: dict):
    """Best-effort (trigger_value, trigger_threshold, trigger_zscore) for the
    event-context block, per evaluator kind. Not every kind has a natural
    zscore -- those get None rather than a fabricated number."""
    kind, params = hypothesis.kind, hypothesis.params
    if kind == "hlp_sentiment_threshold":
        z = raw.get("z_score")
        return z, params.get("z_threshold"), z
    if kind == "liq_momentum":
        return raw.get("vol_5m"), params.get("min_5m_usd"), None
    if kind == "smart_money_top":
        return raw.get("confidence"), params.get("min_confidence"), None
    if kind == "cvd_divergence":
        return raw.get("cvd"), params.get("min_abs_cvd"), None
    if kind == "cross_exchange_liq_leadlag":
        return raw.get("binance_usd"), params.get("min_binance_usd"), None
    return None, None, None


KIND_PARAM_SCHEMA = {
    "hlp_sentiment_threshold": {"z_threshold": "float, e.g. 1.5-3.0"},
    "liq_momentum": {
        "min_5m_usd": "float, min $ liquidated in the trailing 5m window",
        "concentration_ratio": "float 0-1, 5m volume / 15m volume",
    },
    "smart_money_top": {
        "timeframe": "one of 10m, 1h, 24h",
        "min_confidence": "float 0-1",
    },
    "cvd_divergence": {
        "tick_duration": "one of 10m, 1h, 4h, 24h",
        "min_abs_price_change_pct": "float, e.g. 0.01-0.1",
        "min_abs_cvd": "float, min |cumulative tick delta|",
    },
    "cross_exchange_liq_leadlag": {
        "timeframe": "one of 10m, 1h, 4h",
        "min_binance_usd": "float, min $ liquidated on Binance in the window",
        "lead_ratio": "float, how many times bigger Binance's liq $ must be vs HL's",
    },
}
