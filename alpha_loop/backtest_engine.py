"""
Generic event-study evaluator.

Rather than writing a bespoke backtest per hypothesis, every hypothesis
produces a boolean "fired now, predicted direction X" event. This module (a)
evaluates each hypothesis's declarative spec against a cycle's data bundle,
and (b) once enough real time has passed, scores each fired event's forward
return at several horizons against the predicted direction -- sample size,
hit rate, mean/median forward return, a t-stat vs. zero, and a fee-adjusted
mean, mirroring the sensitivity-grid/explicit-fee-assumption discipline used
in research_liq_cascade/backtest.py and the funding-carry analysis doc.

Moon Dev's API itself only keeps a shallow window of historical
ticks/candles/liquidation events (see research_liq_cascade/backtest.py's own
note on this) -- nowhere near enough to backtest most of these ideas against
history. So this loop does NOT pretend to backtest against deep history.
Instead it builds its own live panel over time: every cycle it snapshots
prices and any fired events into alpha_loop.db, and resolves each event's
forward return only once real wall-clock time has elapsed. Statistical power
accumulates the longer the loop runs -- that's the point of it being a loop.
"""

import math
from typing import Optional

import numpy as np

from . import config
from .hypothesis_bank import HORIZONS_MINUTES


def _get_first(d, *keys, default=None):
    for k in keys:
        if isinstance(d, dict) and k in d and d[k] is not None:
            return d[k]
    return default


def eval_hlp_sentiment_threshold(bundle, coin, params):
    data = bundle.get("hlp_sentiment") or {}
    z = _get_first(data, "z_score", "zscore")
    if z is None:
        return None
    thr = params["z_threshold"]
    if z >= thr:
        return {"fired": True, "direction": "up", "raw": {"z_score": z}}
    if z <= -thr:
        return {"fired": True, "direction": "down", "raw": {"z_score": z}}
    return {"fired": False, "direction": None, "raw": {"z_score": z}}


def eval_liq_momentum(bundle, coin, params):
    totals = bundle.get("liquidation_totals") or {}
    windows = totals.get("windows", {})
    w5 = windows.get("5m", {}) or {}
    w15 = windows.get("15m", {}) or {}
    vol5 = _get_first(w5, "total_volume_usd", default=0) or 0
    vol15 = _get_first(w15, "total_volume_usd", default=0) or 0
    if vol15 <= 0:
        return None
    concentration = vol5 / vol15
    fired = vol5 >= params["min_5m_usd"] and concentration >= params["concentration_ratio"]
    long_usd = _get_first(w5, "long_volume_usd", default=0) or 0
    short_usd = _get_first(w5, "short_volume_usd", default=0) or 0
    # More longs got liquidated -> forced selling already happened -> lean down.
    direction = "down" if long_usd > short_usd else "up"
    return {
        "fired": fired,
        "direction": direction if fired else None,
        "raw": {"vol_5m": vol5, "vol_15m": vol15, "concentration": concentration,
                "long_usd": long_usd, "short_usd": short_usd},
    }


def eval_smart_money_top(bundle, coin, params):
    tf = params.get("timeframe", "1h")
    data = (bundle.get("smart_money_signals") or {}).get(tf) or {}
    signals = _get_first(data, "signals", "data", default=[]) or []
    if not signals:
        return {"fired": False, "direction": None, "coin_override": None, "raw": {}}

    def confidence_of(s):
        c = _get_first(s, "confidence", "strength", "score", default=0) or 0
        return c / 100.0 if c > 1 else c

    top = max(signals, key=confidence_of)
    confidence = confidence_of(top)
    sig_coin = _get_first(top, "coin", "symbol", "asset", default=coin)
    direction_raw = str(_get_first(top, "direction", "side", "signal", default="")).upper()
    if "BUY" in direction_raw or "LONG" in direction_raw:
        direction = "up"
    elif "SELL" in direction_raw or "SHORT" in direction_raw:
        direction = "down"
    else:
        direction = None
    fired = confidence >= params["min_confidence"] and direction is not None
    return {
        "fired": fired,
        "direction": direction,
        "coin_override": sig_coin if fired else None,
        "raw": {"confidence": confidence, "coin": sig_coin, "direction_raw": direction_raw},
    }


def _compute_tick_cvd(ticks):
    prices = [_get_first(t, "p", "price", default=0) or 0 for t in ticks]
    if len(prices) < 2:
        return 0, 0.0, prices
    cvd = 0
    last_direction = 0
    for i in range(1, len(prices)):
        diff = prices[i] - prices[i - 1]
        if diff > 0:
            last_direction = 1
        elif diff < 0:
            last_direction = -1
        cvd += last_direction
    price_change_pct = ((prices[-1] - prices[0]) / prices[0] * 100) if prices[0] else 0.0
    return cvd, price_change_pct, prices


def eval_cvd_divergence(bundle, coin, params):
    duration = params.get("tick_duration", "1h")
    ticks = ((bundle.get("ticks") or {}).get(coin) or {}).get(duration) or []
    if len(ticks) < 2:
        return None
    cvd, price_change_pct, _ = _compute_tick_cvd(ticks)
    min_pct = params["min_abs_price_change_pct"]
    min_cvd = params["min_abs_cvd"]
    direction = None
    fired = False
    if price_change_pct > min_pct and cvd < -min_cvd:
        direction, fired = "down", True  # bearish divergence: price up, sellers aggressive
    elif price_change_pct < -min_pct and cvd > min_cvd:
        direction, fired = "up", True    # bullish divergence: price down, buyers aggressive
    return {"fired": fired, "direction": direction, "raw": {"price_change_pct": price_change_pct, "cvd": cvd}}


def eval_cross_exchange_liq_leadlag(bundle, coin, params):
    tf = params.get("timeframe", "10m")
    ex = bundle.get("exchange_liquidations") or {}
    binance = (ex.get("binance") or {}).get(tf, {}) or {}
    hl = (ex.get("hyperliquid") or {}).get(tf, {}) or {}

    def stats_of(d):
        s = _get_first(d, "stats", default=d) or {}
        usd = _get_first(s, "total_value_usd", "total_usd", default=0) or 0
        long_c = _get_first(s, "long_count", "longs", default=0) or 0
        short_c = _get_first(s, "short_count", "shorts", default=0) or 0
        return usd, long_c, short_c

    b_usd, b_long, b_short = stats_of(binance)
    h_usd, _, _ = stats_of(hl)
    fired = b_usd >= params["min_binance_usd"] and (h_usd == 0 or b_usd >= h_usd * params["lead_ratio"])
    direction = "down" if b_long > b_short else "up"
    return {
        "fired": fired,
        "direction": direction if fired else None,
        "raw": {"binance_usd": b_usd, "hl_usd": h_usd, "binance_long": b_long, "binance_short": b_short},
    }


KIND_EVALUATORS = {
    "hlp_sentiment_threshold": eval_hlp_sentiment_threshold,
    "liq_momentum": eval_liq_momentum,
    "smart_money_top": eval_smart_money_top,
    "cvd_divergence": eval_cvd_divergence,
    "cross_exchange_liq_leadlag": eval_cross_exchange_liq_leadlag,
}


def evaluate_hypothesis(hypothesis, bundle) -> Optional[dict]:
    """Returns None if data was missing, else {"fired", "direction", "raw", ["coin_override"]}."""
    fn = KIND_EVALUATORS.get(hypothesis.kind)
    if fn is None:
        return None
    try:
        return fn(bundle, hypothesis.coin, hypothesis.params)
    except Exception:
        return None


def t_stat(values: np.ndarray) -> float:
    n = len(values)
    if n < 2:
        return float("nan")
    std = values.std(ddof=1)
    if std == 0:
        return float("nan")
    return float(values.mean() / (std / math.sqrt(n)))


def summarize_outcomes(returns: np.ndarray, predicted_hits: np.ndarray) -> dict:
    """returns: forward returns (signed, in the predicted direction). predicted_hits: bool array."""
    n = len(returns)
    if n == 0:
        return {"n": 0}
    fee_adjusted = returns - config.ROUND_TRIP_FEE_FRACTION
    return {
        "n": n,
        "hit_rate": float(predicted_hits.mean()),
        "mean_return": float(returns.mean()),
        "median_return": float(np.median(returns)),
        "t_stat": t_stat(returns),
        "mean_return_fee_adjusted": float(fee_adjusted.mean()),
        "t_stat_fee_adjusted": t_stat(fee_adjusted),
    }
