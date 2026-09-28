"""
Builds the structured, machine-readable per-cycle report and a Discord-
friendly rendering of it. Nothing here computes new statistics -- it only
assembles what backtest_engine.evaluate_evidence() and the research-loop
bookkeeping already produced into one consistent shape, so a cycle with
n=1 says "insufficient_n" instead of printing a hit rate as if it meant
something.
"""

import numpy as np

from . import store
from .backtest_engine import evaluate_evidence
from .hypothesis_bank import HORIZONS_MINUTES

STATUS_MARKER = {
    "meets_all_gates": "✅",
    "insufficient_n_but_promising": "\U0001f440",  # 👀 -- worth watching, not yet proven
    "insufficient_evidence": "⚠️",
    "insufficient_n": "·",
}
STATUS_ORDER = {"meets_all_gates": 0, "insufficient_n_but_promising": 1, "insufficient_evidence": 2,
                "insufficient_n": 3, "no_data": 4}


def build_strategy_reports(conn):
    """One row per (hypothesis, horizon) that has at least one resolved outcome."""
    rows = []
    for h in store.active_hypotheses(conn):
        for horizon in HORIZONS_MINUTES:
            outcomes = store.outcomes_for_hypothesis(conn, h.id, horizon)
            if not outcomes:
                continue
            gross = np.array([o["forward_return"] for o in outcomes])
            net = np.array([o["net_return"] for o in outcomes])
            hits = np.array([bool(o["hit"]) for o in outcomes])
            mfe_vals = [o["mfe"] for o in outcomes if o["mfe"] is not None]
            mae_vals = [o["mae"] for o in outcomes if o["mae"] is not None]
            mfe = np.array(mfe_vals) if mfe_vals else None
            mae = np.array(mae_vals) if mae_vals else None

            evidence = evaluate_evidence(gross, hits, net, mfe, mae)
            evidence.update({
                "name": h.name, "kind": h.kind, "coin": h.coin,
                "horizon": horizon, "source": h.source,
            })
            rows.append(evidence)
    return rows


def build_cycle_report(conn, cycle: int, now_iso: str, data_window: dict, events_fired: int,
                        research_block: dict) -> dict:
    strategies = build_strategy_reports(conn)
    return {
        "cycle": cycle,
        "timestamp_utc": now_iso,
        "data_window": data_window,
        "events_fired": events_fired,
        **research_block,
        "strategies": strategies,
    }


def format_discord_summary(report: dict) -> str:
    lines = [
        f"cycle {report['cycle']} -- events_fired={report['events_fired']} "
        f"hyp_generated={report.get('hypotheses_generated', 0)} "
        f"hyp_promoted={report.get('hypotheses_promoted', 0)} "
        f"new_research_leads={report.get('new_research_leads', 0)}",
    ]
    if report.get("why_no_new_leads"):
        lines.append(f"why_no_new_hypotheses: {report['why_no_new_leads']}")

    if not report["strategies"]:
        lines.append("no resolved outcomes yet")
        return "\n".join(lines)

    for s in sorted(report["strategies"], key=lambda r: (STATUS_ORDER.get(r["status"], 9), -r["n"])):
        marker = STATUS_MARKER.get(s["status"], "?")
        hit = f"{s['hit_rate']*100:.0f}%" if s.get("hit_rate") is not None else "n/a"
        lines.append(
            f"{marker} {s['name'][:42]:42} [{s['horizon']:>3}] n={s['n']:<4} "
            f"status={s['status']:20} hit={hit:>4} net={s['mean_return_net']:+.5f}"
        )
    return "\n".join(lines)
