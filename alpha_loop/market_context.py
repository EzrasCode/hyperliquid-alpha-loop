"""
Lightweight market-context tagging for events, computed entirely from this
loop's own accumulated price_snapshots panel -- no extra API calls. Feeds
the event-context and conditioning/segmentation requests: aggregate stats
hide regime dependence (a signal that only works in high-vol NY sessions
looks mediocre-but-real in an aggregate average).

This is a simple heuristic, not a real regime-detection model -- it exists
to let report_top_ideas.py segment by something rather than nothing. Every
function returns None/"insufficient_history" rather than a fabricated number
when there isn't yet enough accumulated history to say anything, which will
be the case for the first several days of running.
"""

import math
from datetime import datetime, timezone

from . import config


def session_label(dt: datetime) -> str:
    hour = dt.astimezone(timezone.utc).hour
    for name, start, end in config.SESSION_WINDOWS_UTC:
        if start <= hour < end:
            return name
    return "Unknown"


def _prices_between(conn, coin, start_iso, end_iso):
    rows = conn.execute(
        "SELECT ts, price FROM price_snapshots WHERE coin = ? AND ts >= ? AND ts <= ? ORDER BY ts ASC",
        (coin, start_iso, end_iso),
    ).fetchall()
    return [r["price"] for r in rows]


def _realized_vol(prices) -> float | None:
    if len(prices) < 3:
        return None
    log_returns = [math.log(prices[i] / prices[i - 1]) for i in range(1, len(prices)) if prices[i - 1] > 0]
    if len(log_returns) < 2:
        return None
    mean = sum(log_returns) / len(log_returns)
    var = sum((r - mean) ** 2 for r in log_returns) / (len(log_returns) - 1)
    return math.sqrt(var)


def market_context(conn, coin: str, at_time: datetime) -> dict:
    """Returns {session, vol_lookback_hours, realized_vol, vol_percentile,
    regime_label} -- vol_percentile and regime_label are None/"insufficient_history"
    until enough of the loop's own accumulated history exists."""
    from datetime import timedelta

    lookback_start = (at_time - timedelta(hours=config.VOL_LOOKBACK_HOURS)).isoformat()
    at_iso = at_time.isoformat()
    current_prices = _prices_between(conn, coin, lookback_start, at_iso)
    current_vol = _realized_vol(current_prices)

    context = {
        "session": session_label(at_time),
        "vol_lookback_hours": config.VOL_LOOKBACK_HOURS,
        "realized_vol": current_vol,
        "vol_percentile": None,
        "regime_label": "insufficient_history",
    }
    if current_vol is None:
        return context

    # Build a distribution of same-length rolling-window vols from all
    # earlier accumulated history to rank the current window against.
    all_rows = conn.execute(
        "SELECT ts, price FROM price_snapshots WHERE coin = ? AND ts <= ? ORDER BY ts ASC",
        (coin, at_iso),
    ).fetchall()
    if len(all_rows) < 4:
        return context

    window_size = max(3, len(current_prices))
    historical_vols = []
    for i in range(window_size, len(all_rows)):
        window = [all_rows[j]["price"] for j in range(i - window_size, i)]
        v = _realized_vol(window)
        if v is not None:
            historical_vols.append(v)

    if len(historical_vols) < config.MIN_HISTORY_WINDOWS_FOR_PERCENTILE:
        return context

    below = sum(1 for v in historical_vols if v <= current_vol)
    percentile = 100.0 * below / len(historical_vols)
    context["vol_percentile"] = percentile

    # Crude trend-vs-range heuristic: how many standard deviations the net
    # move over the lookback window is from zero, using realized vol as the
    # per-step scale. Not a real regime model -- documented as such above.
    if len(current_prices) >= 2 and current_vol > 0:
        net_log_return = math.log(current_prices[-1] / current_prices[0])
        trend_z = net_log_return / (current_vol * math.sqrt(len(current_prices)))
        context["regime_label"] = "trending" if abs(trend_z) >= 1.0 else "ranging"
    return context
