"""
The alpha-mining loop. Read-only research: no order placement, no private
keys, no live capital anywhere in this module or anything it imports.

Deployed via GitHub Actions (.github/workflows/alpha_loop.yml) on a 5-minute
cron schedule, each run doing exactly one cycle against a fresh checkout:

    python -m alpha_loop.loop --once

`--once` is the only mode used in production; the plain `while True` form
below exists for local development.

Each cycle:
  1. Pull one shared data bundle (prices, HLP sentiment, liquidation totals,
     smart-money signals, ticks, per-exchange liquidations) -- shared across
     all hypotheses so we don't refetch the same endpoint N times.
  2. Snapshot prices for the universe into the price panel (this loop's own
     accumulating history -- see backtest_engine.py's docstring).
  3. Evaluate every active hypothesis; for each that fires, tag it with
     market context (session/regime/vol percentile) and trigger details,
     and record an event.
  4. Resolve any (event, horizon) pairs whose forward-return window has
     elapsed: gross/net return, hit, and MFE/MAE over the accumulated price
     path between event time and the horizon target.
  5. Every IDEA_GEN_EVERY_N_CYCLES, ask for new hypothesis parameterizations
     -- tracking not just how many were accepted, but why any were rejected
     or why zero came back.
  6. Every RESEARCH_SCOUT_EVERY_N_CYCLES, check arXiv, Semantic Scholar,
     Quantocracy, Reddit, and GitHub for new candidate leads.
  7. Assemble the structured cycle report (reporting.py), append it to
     cycle_reports.jsonl, write a decision-log line, and post to Discord.
"""

import argparse
import json
import sys
import time
import traceback
from datetime import datetime, timedelta, timezone

from . import config, market_context, reporting, research_scout, store
from .backtest_engine import compute_mfe_mae, evaluate_hypothesis
from .data_cache import CachedMoonDevAPI
from .discord_notify import send_cycle_summary, send_research_leads
from .hypothesis_bank import HORIZONS_MINUTES, SEED_HYPOTHESES, extract_trigger_fields
from .idea_generator import propose_new_hypotheses


def fetch_bundle(api: CachedMoonDevAPI) -> dict:
    bundle = {}

    prices_resp = api.call("get_prices") or {}
    bundle["prices"] = {
        coin: float(price)
        for coin, price in (prices_resp.get("prices") or {}).items()
        if coin in config.UNIVERSE
    }
    bundle["funding_rates"] = {
        coin: prices_resp.get("funding_rates", {}).get(coin)
        for coin in config.UNIVERSE
    }
    bundle["prices_timestamp"] = prices_resp.get("timestamp")

    bundle["hlp_sentiment"] = api.call("get_hlp_sentiment") or {}
    bundle["liquidation_totals"] = api.call("get_all_liquidation_totals") or {}

    bundle["smart_money_signals"] = {}
    for tf in ("10m", "1h", "24h"):
        bundle["smart_money_signals"][tf] = api.call("get_smart_money_signals", tf) or {}

    bundle["ticks"] = {}
    bundle["tick_counts"] = {}
    for coin in config.UNIVERSE:
        tick_resp = api.call("get_ticks", coin, "1h", limit=5000) or {}
        ticks = tick_resp.get("ticks", [])
        bundle["ticks"][coin] = {"1h": ticks}
        bundle["tick_counts"][coin] = len(ticks)

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
    resolved_count = 0
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
            gross_return = forward_return if predicted_up else -forward_return
            net_return = gross_return - config.ROUND_TRIP_COST_FRACTION
            hit = (forward_return > 0) == predicted_up

            path = store.price_path_between(conn, row["coin"], row["event_time"], target_time.isoformat())
            excursion = compute_mfe_mae(row["event_time"], path, price_at_event, row["predicted_direction"])

            store.record_outcome(
                conn, event_id, horizon, forward_price, gross_return, net_return, hit,
                mfe=excursion["mfe"], mae=excursion["mae"],
                time_to_mfe_minutes=excursion["time_to_mfe_minutes"],
                time_to_mae_minutes=excursion["time_to_mae_minutes"],
            )
            resolved_count += 1
    return resolved_count


def run_cycle(api: CachedMoonDevAPI, cycle: int):
    fetch_start = datetime.now(timezone.utc)
    with store.connect() as conn:
        for h in SEED_HYPOTHESES:
            store.upsert_hypothesis(conn, h)

        bundle = fetch_bundle(api)
        now = datetime.now(timezone.utc)

        for coin, price in bundle["prices"].items():
            store.record_price_snapshot(conn, coin, now.isoformat(), price)

        fired_count, evaluated_count = 0, 0
        for h in store.active_hypotheses(conn):
            evaluated_count += 1
            result = evaluate_hypothesis(h, bundle)
            if not result or not result.get("fired"):
                continue
            coin = result.get("coin_override") or h.coin
            price = bundle["prices"].get(coin)
            if price is None:
                continue

            ctx = market_context.market_context(conn, coin, now)
            ctx["funding_rate"] = bundle["funding_rates"].get(coin)
            ctx["tick_count"] = bundle["tick_counts"].get(coin)
            if bundle.get("prices_timestamp"):
                try:
                    data_ts = datetime.fromisoformat(str(bundle["prices_timestamp"]).replace("Z", "+00:00"))
                    ctx["data_latency_ms"] = (now - data_ts).total_seconds() * 1000
                except ValueError:
                    ctx["data_latency_ms"] = None

            trigger_value, trigger_threshold, trigger_zscore = extract_trigger_fields(h, result.get("raw", {}))

            store.record_event(
                conn, h.id, coin, result["direction"], price, result.get("raw", {}),
                event_time=now.isoformat(), context=ctx,
                trigger_value=trigger_value, trigger_threshold=trigger_threshold, trigger_zscore=trigger_zscore,
            )
            fired_count += 1

        resolved_count = resolve_due_outcomes(conn, now)

        hyp_generated = hyp_promoted = 0
        idea_rejected, why_no_new_leads = [], None
        if cycle % config.IDEA_GEN_EVERY_N_CYCLES == 0:
            context_text = reporting.format_discord_summary(
                reporting.build_cycle_report(conn, cycle, now.isoformat(), {}, 0, {})
            )
            idea_result = propose_new_hypotheses(context_text)
            hyp_generated = idea_result["raw_count"]
            idea_rejected = idea_result["rejected"]
            why_no_new_leads = idea_result["why_no_new_leads"]
            for candidate in idea_result["accepted"]:
                if store.upsert_hypothesis(conn, candidate):
                    hyp_promoted += 1
                else:
                    idea_rejected.append({"item": candidate.name, "reason": "duplicate of existing hypothesis"})
            if hyp_generated and not hyp_promoted and why_no_new_leads is None:
                why_no_new_leads = "all accepted candidates were duplicates of existing hypotheses"

        new_leads = []
        if cycle % config.RESEARCH_SCOUT_EVERY_N_CYCLES == 0:
            for lead in research_scout.fetch_all_candidates():
                if store.record_research_lead(
                    conn, lead["source"], lead["external_id"], lead["title"],
                    lead["summary"], lead["link"], lead["published"],
                ):
                    new_leads.append(lead)
            if new_leads:
                write_research_leads_doc(now, new_leads)
                send_research_leads(new_leads)

        research_block = {
            "hypotheses_generated": hyp_generated,
            "hypotheses_promoted": hyp_promoted,
            "hypotheses_rejected": idea_rejected,
            "why_no_new_leads": why_no_new_leads,
            "new_research_leads": len(new_leads),
            "compute_budget_used": {
                "hypotheses_evaluated": evaluated_count,
                "outcomes_resolved": resolved_count,
            },
        }
        data_window = {"start": fetch_start.isoformat(), "end": now.isoformat()}

        report = reporting.build_cycle_report(conn, cycle, now.isoformat(), data_window, fired_count, research_block)
        summary = reporting.format_discord_summary(report)

        store.append_cycle_log(conn, cycle, summary)
        write_decision_log_entry(now, summary)
        append_cycle_report_jsonl(report)
        send_cycle_summary(cycle, summary)
        return summary


def write_decision_log_entry(now: datetime, summary: str):
    config.DECISION_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    header_needed = not config.DECISION_LOG_PATH.exists()
    with open(config.DECISION_LOG_PATH, "a", encoding="utf-8") as f:
        if header_needed:
            f.write(
                "# Alpha loop decision log\n\n"
                "Append-only human-readable summary. The full structured record for "
                "every cycle (per-strategy statistics, gate reasons, MFE/MAE, research-"
                "loop transparency) lives in cycle_reports.jsonl -- see "
                "alpha_loop_overview_20260927.md.\n\n"
            )
        f.write(f"## {now.strftime('%Y-%m-%d %H:%M UTC')}\n\n{summary}\n\n")


def append_cycle_report_jsonl(report: dict):
    path = config.REPO_ROOT / "docs" / "research" / "alpha_loop" / "cycle_reports.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(report, default=str) + "\n")


def write_research_leads_doc(now: datetime, leads: list):
    config.RESEARCH_LEADS_DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    header_needed = not config.RESEARCH_LEADS_DOC_PATH.exists()
    with open(config.RESEARCH_LEADS_DOC_PATH, "a", encoding="utf-8") as f:
        if header_needed:
            f.write(
                "# Research leads\n\n"
                "Append-only. Candidate leads surfaced by research_scout.py from "
                "arXiv, Semantic Scholar, Quantocracy, and GitHub -- anything that "
                "might be relevant to this loop's signals (Reddit is defined but "
                "inactive, see research_scout.py). Nothing here is auto-converted "
                "into a testable signal -- that still requires a human to write a "
                "new evaluator function in backtest_engine.py.\n\n"
            )
        f.write(f"## {now.strftime('%Y-%m-%d %H:%M UTC')}\n\n")
        for lead in leads:
            published = (lead.get("published") or "")[:10]
            f.write(f"- **[{lead['source']}]** {lead['title']} ({published})\n  {lead['link']}\n  {lead['summary'][:300]}\n\n")


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
