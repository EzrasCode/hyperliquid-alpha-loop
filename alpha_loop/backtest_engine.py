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
from datetime import datetime
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


def compute_mfe_mae(event_time_iso: str, price_path: list, entry_price: float, predicted_direction: str) -> dict:
    """price_path: chronological list of (ts_iso, price) covering the window
    from event time to a horizon's target time. Returns signed excursions
    (positive=favorable in the predicted direction) and how long each took to
    reach, in minutes from the event. All None if the path is empty -- e.g.
    right after an event fires, before any later snapshots exist yet."""
    empty = {"mfe": None, "mae": None, "time_to_mfe_minutes": None, "time_to_mae_minutes": None}
    if not price_path or not entry_price:
        return empty

    sign = 1.0 if predicted_direction == "up" else -1.0
    event_time = datetime.fromisoformat(event_time_iso)
    best_favorable, best_adverse = float("-inf"), float("inf")
    t_mfe = t_mae = None
    for ts_iso, price in price_path:
        excursion = sign * (price / entry_price - 1.0)
        minutes = (datetime.fromisoformat(ts_iso) - event_time).total_seconds() / 60.0
        if excursion > best_favorable:
            best_favorable, t_mfe = excursion, minutes
        if excursion < best_adverse:
            best_adverse, t_mae = excursion, minutes
    return {"mfe": best_favorable, "mae": best_adverse, "time_to_mfe_minutes": t_mfe, "time_to_mae_minutes": t_mae}


def wilson_ci(hit_count: int, n: int, z: float = 1.96):
    """Wilson score interval for a hit rate -- much better-behaved than a
    normal-approximation CI at small n, though still meaningless below
    config.MIN_N_FOR_SIGNIFICANCE."""
    if n == 0:
        return None, None
    phat = hit_count / n
    denom = 1 + z * z / n
    center = phat + z * z / (2 * n)
    margin = z * math.sqrt(phat * (1 - phat) / n + z * z / (4 * n * n))
    return max(0.0, (center - margin) / denom), min(1.0, (center + margin) / denom)


def two_sided_p_value(t: float) -> "float | None":
    """Normal approximation to the two-sided p-value for a t-stat. This is
    an approximation, not the exact Student's t distribution -- reasonable
    once n is at or above config.MIN_N_FOR_SIGNIFICANCE (the regime this is
    actually used in), not claimed to be exact at small n."""
    from statistics import NormalDist

    if t is None or math.isnan(t):
        return None
    return 2 * (1 - NormalDist().cdf(abs(t)))


def block_bootstrap_p(returns: np.ndarray, rng: "np.random.Generator" = None) -> "float | None":
    """Contiguous-block resampling (not i.i.d. resampling) so the bootstrap
    respects short-range autocorrelation in the return series, per
    config.BOOTSTRAP_BLOCK_SIZE. Tests: across resamples of this loop's own
    observed data, what fraction land on the opposite side of zero from the
    observed mean -- a nonparametric check of how fragile the sign of the
    mean return is, not a from-scratch null-hypothesis simulation."""
    n = len(returns)
    if n < 2:
        return None
    rng = rng or np.random.default_rng()
    block = min(config.BOOTSTRAP_BLOCK_SIZE, n)
    n_blocks = math.ceil(n / block)
    observed_mean = returns.mean()
    boot_means = np.empty(config.BOOTSTRAP_ITERATIONS)
    max_start = n - block
    for b in range(config.BOOTSTRAP_ITERATIONS):
        starts = rng.integers(0, max_start + 1, size=n_blocks) if max_start > 0 else np.zeros(n_blocks, dtype=int)
        resampled = np.concatenate([returns[s:s + block] for s in starts])[:n]
        boot_means[b] = resampled.mean()
    p_one_sided = float((boot_means <= 0).mean()) if observed_mean >= 0 else float((boot_means >= 0).mean())
    return min(1.0, 2 * p_one_sided)


def max_drawdown(returns: np.ndarray) -> float:
    """Max drawdown of the additive (per-trade, non-compounding) cumulative
    return curve, in chronological order."""
    if len(returns) == 0:
        return 0.0
    curve = np.cumsum(returns)
    running_max = np.maximum.accumulate(curve)
    drawdown = curve - running_max
    return float(drawdown.min())


def sign_consistency(returns: np.ndarray, n_subperiods: int = 3) -> "tuple[bool, list]":
    """Splits returns (already in chronological order) into n_subperiods
    contiguous groups and checks whether the sign of the overall mean is
    matched by at least 2 of them. Guards against a mean that's only
    positive because of one lucky early sub-period."""
    n = len(returns)
    if n < n_subperiods * 2:
        return False, []
    chunks = np.array_split(returns, n_subperiods)
    overall_sign = np.sign(returns.mean())
    chunk_means = [float(c.mean()) for c in chunks if len(c) > 0]
    matches = sum(1 for m in chunk_means if np.sign(m) == overall_sign)
    return matches >= max(2, len(chunk_means) - 1), chunk_means


def evaluate_evidence(
    gross_returns: np.ndarray,
    hits: np.ndarray,
    net_returns: np.ndarray,
    mfe: "np.ndarray | None" = None,
    mae: "np.ndarray | None" = None,
) -> dict:
    """The statistical-validity + execution-realism + forward-path blocks,
    all in one place, plus a gating `status`. Arrays must be aligned and in
    chronological order. Everything here is computed from what this loop has
    actually observed -- nothing here is asserted true, only "meets/doesn't
    meet the stated gates so far"."""
    n = len(gross_returns)
    if n == 0:
        return {"n": 0, "status": "no_data"}

    hit_count = int(hits.sum())
    hit_rate = float(hits.mean())
    ci_low, ci_high = wilson_ci(hit_count, n)

    wins = gross_returns[gross_returns > 0]
    losses = gross_returns[gross_returns < 0]
    avg_win = float(wins.mean()) if len(wins) else None
    avg_loss = float(losses.mean()) if len(losses) else None
    gross_profit = float(wins.sum()) if len(wins) else 0.0
    gross_loss = float(-losses.sum()) if len(losses) else 0.0
    profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else (float("inf") if gross_profit > 0 else None)

    if n >= 2:
        t = t_stat(gross_returns)
        p_value = two_sided_p_value(t)
        std_return = float(gross_returns.std(ddof=1))
        sharpe = float(gross_returns.mean() / std_return) if std_return > 0 else None
        consistent, subperiod_means = sign_consistency(gross_returns)
        bootstrap_p = block_bootstrap_p(gross_returns)
        t_status = "computed"
    else:
        t, p_value, std_return, sharpe, bootstrap_p = float("nan"), None, None, None, None
        consistent, subperiod_means = False, []
        t_status = "insufficient_n"

    result = {
        "n": n,
        "mean_return_gross": float(gross_returns.mean()),
        "median_return": float(np.median(gross_returns)),
        "std_return": std_return,
        "t_stat": t if t_status == "computed" else None,
        "t_stat_status": t_status,
        "p_value": p_value,
        "hit_rate": hit_rate,
        "hit_rate_ci_low": ci_low,
        "hit_rate_ci_high": ci_high,
        "avg_win": avg_win,
        "avg_loss": avg_loss,
        "profit_factor": profit_factor,
        "sharpe_per_trade": sharpe,
        "max_drawdown": max_drawdown(gross_returns),
        "bootstrap_p": bootstrap_p,
        "sign_consistent_subperiods": consistent,
        "subperiod_means": subperiod_means,
        "mean_return_net": float(net_returns.mean()),
        "taker_fee_bps": config.TAKER_FEE_BPS,
        "slippage_bps": config.SLIPPAGE_BPS,
    }

    if mfe is not None and mae is not None and len(mfe) > 0 and len(mae) > 0:
        mfe_mean, mae_mean = float(np.mean(mfe)), float(np.mean(mae))
        result["mfe_mean"] = mfe_mean
        result["mae_mean"] = mae_mean
        result["mfe_mae_ratio"] = (mfe_mean / abs(mae_mean)) if mae_mean != 0 else None
    else:
        result["mfe_mean"] = result["mae_mean"] = result["mfe_mae_ratio"] = None

    reasons = []
    if n < config.MIN_N_FOR_SIGNIFICANCE:
        reasons.append(f"n={n} < {config.MIN_N_FOR_SIGNIFICANCE}")
    if t_status != "computed" or t is None or math.isnan(t) or abs(t) < config.MIN_ABS_T_STAT:
        reasons.append(f"|t|<{config.MIN_ABS_T_STAT}")
    if result["mean_return_net"] <= 0:
        reasons.append("net_return<=0")
    if result["mfe_mae_ratio"] is not None and result["mfe_mae_ratio"] <= config.MIN_MFE_MAE_RATIO:
        reasons.append(f"mfe/mae<={config.MIN_MFE_MAE_RATIO}")
    if bootstrap_p is None or bootstrap_p >= config.MAX_BOOTSTRAP_P:
        reasons.append(f"bootstrap_p>={config.MAX_BOOTSTRAP_P}")
    if not consistent:
        reasons.append("sign_inconsistent_across_subperiods")

    result["status"] = "insufficient_n" if n < config.MIN_N_FOR_SIGNIFICANCE else (
        "meets_all_gates" if not reasons else "insufficient_evidence"
    )
    result["gate_failure_reasons"] = reasons
    return result
