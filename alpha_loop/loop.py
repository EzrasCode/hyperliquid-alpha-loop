"""
The alpha-mining loop. Read-only research: no order placement, no private
keys, no live capital anywhere in this module or anything it imports.

Deployed via GitHub Actions (.github/workflows/alpha_loop.yml) on a 5-minute
cron schedule, each run doing exactly one cycle against a fresh checkout:

    python -m alpha_loop.loop --once

`--once` is the only mode used in production; the plain `while True` form
below exists for local development where you want it to keep running without
re-invoking python each time.

Each cycle:
  1. Pull one shared data bundle (prices, HLP sentiment, liquidation totals,
     smart-money signals, ticks, per-exchange liquidations) -- shared across
     all hypotheses so we don't refetch the same endpoint N times.
  2. Snapshot prices for the universe into the price panel (this loop's own
     accumulating history, since the API's own history is shallow -- see
     backtest_engine.py's docstring).
  3. Evaluate every active hypothesis against the bundle; record an event for
     each one that fired.
  4. Resolve any (event, horizon) pairs whose forward-return window has now
     elapsed, using the accumulated price panel.
  5. Every IDEA_GEN_EVERY_N_CYCLES, ask the idea generator for new
     hypothesis parameterizations and store any that validate and aren't
     duplicates.
  6. Append one line to the append-only decision log and post the cycle
     summary to Discord.
"""

import argparse
import sys
import time
import traceback
from datetime import datetime, timedelta, timezone

import numpy as np

from . import config, store
from .backtest_engine import evaluate_hypothesis, summarize_outcomes
from .data_cache import CachedMoonDevAPI
from .discord_notify import send_cycle_summary
from .hypothesis_bank import HORIZONS_MINUTES, SEED_HYPOTHESES
from .idea_generator import propose_new_hypotheses


def fetch_bundle(api: CachedMoonDevAPI) -> dict:
    bundle = {}

    prices_resp = api.call("get_prices") or {}
    bundle["prices"] = {
        coin: float(price)
        for coin, price in (prices_resp.get("prices") or {}).items()
        if coin in config.UNIVERSE
    }

    bundle["hlp_sentiment"] = api.call("get_hlp_sentiment") or {}
    bundle["liquidation_totals"] = api.call("get_all_liquidation_totals") or {}

    bundle["smart_money_signals"] = {}
    for tf in ("10m", "1h", "24h"):
        bundle["smart_money_signals"][tf] = api.call("get_smart_money_signals", tf) or {}

    bundle["ticks"] = {}
    for coin in config.UNIVERSE:
        tick_resp = api.call("get_ticks", coin, "1h", limit=5000) or {}
        bundle["ticks"][coin] = {"1h": tick_resp.get("ticks", [])}

    bundle["exchange_liquidations"] = {}
    for exchange, method in (
        ("hyperliquid", "get_liquidations"),
        ("binance", "get_binance_liquidations"),
        ("bybit", "get_bybit_liquidations"),
        ("okx", "get_okx_liquidations"),
    ):
        data = api.call(method, "10m") or {}
        stats = data.get("stats", data) if isinstance(data, dict) else {}
        bundle["exchange_liquidations"][exchange] = {"10m": stats}

    return bundle


def resolve_due_outcomes(conn, now: datetime):
    rows = store.unresolved_event_horizons(conn)
    for row in rows:
        event_id = row["event_id"]
        event_time = datetime.fromisoformat(row["event_time"])
        already_resolved = store.resolved_horizons_for_event(conn, event_id)
        for horizon, minutes in HORIZONS_MINUTES.items():
            if horizon in already_resolved:
                continue
            target_time = event_time + timedelta(minutes=minutes)
            if target_time > now:
                continue
            found = store.nearest_price_at_or_after(conn, row["coin"], target_time.isoformat())
            if found is None:
                continue
            _, forward_price = found
            price_at_event = row["price_at_event"]
            forward_return = (forward_price / price_at_event) - 1.0
            predicted_up = row["predicted_direction"] == "up"
            hit = (forward_return > 0) == predicted_up
            signed_return = forward_return if predicted_up else -forward_return
            store.record_outcome(conn, event_id, horizon, forward_price, signed_return, hit)


def cycle_summary_text(conn) -> str:
    lines = []
    for h in store.active_hypotheses(conn):
        for horizon in HORIZONS_MINUTES:
            outcomes = store.outcomes_for_hypothesis(conn, h.id, horizon)
            if not outcomes:
                continue
            returns = np.array([o["forward_return"] for o in outcomes])
            hits = np.array([bool(o["hit"]) for o in outcomes])
            stats = summarize_outcomes(returns, hits)
            lines.append(
                f"{h.name} [{horizon}]: n={stats['n']} hit_rate={stats['hit_rate']:.2f} "
                f"mean_return={stats['mean_return']:+.4f} t={stats['t_stat']:.2f}"
            )
    return "\n".join(lines) if lines else "no resolved outcomes yet"


def run_cycle(api: CachedMoonDevAPI, cycle: int):
    now = datetime.now(timezone.utc)
    with store.connect() as conn:
        for h in SEED_HYPOTHESES:
            store.upsert_hypothesis(conn, h)

        bundle = fetch_bundle(api)

        for coin, price in bundle["prices"].items():
            store.record_price_snapshot(conn, coin, now.isoformat(), price)

        fired_count = 0
        for h in store.active_hypotheses(conn):
            result = evaluate_hypothesis(h, bundle)
            if not result or not result.get("fired"):
                continue
            coin = result.get("coin_override") or h.coin
            price = bundle["prices"].get(coin)
            if price is None:
                continue
            store.record_event(
                conn, h.id, coin, result["direction"], price, result.get("raw", {}),
                event_time=now.isoformat(),
            )
            fired_count += 1

        resolve_due_outcomes(conn, now)

        new_hypotheses_added = 0
        if cycle % config.IDEA_GEN_EVERY_N_CYCLES == 0:
            context = cycle_summary_text(conn)
            for candidate in propose_new_hypotheses(context):
                if store.upsert_hypothesis(conn, candidate):
                    new_hypotheses_added += 1

        summary = (
            f"cycle {cycle}: {fired_count} events fired, "
            f"{new_hypotheses_added} new hypotheses added\n{cycle_summary_text(conn)}"
        )
        store.append_cycle_log(conn, cycle, summary)
        write_decision_log_entry(now, summary)
        send_cycle_summary(cycle, summary)
        return summary


def write_decision_log_entry(now: datetime, summary: str):
    config.DECISION_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    header_needed = not config.DECISION_LOG_PATH.exists()
    with open(config.DECISION_LOG_PATH, "a", encoding="utf-8") as f:
        if header_needed:
            f.write(
                "# Alpha loop decision log\n\n"
                "Append-only. One entry per cycle that changed the hypothesis "
                "bank or moved a hypothesis's stats meaningfully. See "
                "alpha_loop_overview_20260927.md for methodology.\n\n"
            )
        f.write(f"## {now.strftime('%Y-%m-%d %H:%M UTC')}\n\n{summary}\n\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="Run a single cycle and exit.")
    args = parser.parse_args()

    api = CachedMoonDevAPI()
    if not api.has_key:
        print("ERROR: MOONDEV_API_KEY not set (env var or GitHub secret).")
        sys.exit(1)

    with store.connect() as conn:
        cycle = store.next_cycle_number(conn)

    while True:
        try:
            summary = run_cycle(api, cycle)
            print(summary)
        except Exception:
            traceback.print_exc()
        if args.once:
            break
        cycle += 1
        time.sleep(config.CYCLE_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
