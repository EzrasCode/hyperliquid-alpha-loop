"""
Ranked leaderboard of hypotheses by evidence gate status -- the human
review surface. A row is never printed as if it means something below
config.MIN_N_FOR_SIGNIFICANCE; it's explicitly labeled "insufficient_n".
Also breaks each hypothesis down by regime/session, since a signal that
only works in one regime looks mediocre-but-real in the aggregate.

Usage: python -m alpha_loop.report_top_ideas
"""

import json
from collections import defaultdict

import numpy as np

from . import store
from .backtest_engine import evaluate_evidence
from .hypothesis_bank import HORIZONS_MINUTES
from .reporting import STATUS_ORDER, build_strategy_reports


def print_leaderboard(conn):
    rows = build_strategy_reports(conn)
    if not rows:
        print("No resolved outcomes yet. Let `python -m alpha_loop.loop` run for a while first.")
        return

    ranked = sorted(rows, key=lambda r: (STATUS_ORDER.get(r["status"], 9), -abs(r.get("t_stat") or 0)))

    header = (
        f"{'hypothesis':45} {'horizon':7} {'status':20} {'n':>5} {'hit%':>6} "
        f"{'net_ret':>9} {'t':>6} {'p':>7} {'mfe/mae':>8} {'gates_failed'}"
    )
    print(header)
    print("-" * len(header))
    for s in ranked:
        t = f"{s['t_stat']:.2f}" if s.get("t_stat") is not None else "n/a"
        p = f"{s['p_value']:.3f}" if s.get("p_value") is not None else "n/a"
        ratio = f"{s['mfe_mae_ratio']:.2f}" if s.get("mfe_mae_ratio") is not None else "n/a"
        reasons = ", ".join(s.get("gate_failure_reasons", [])) or "-"
        print(
            f"{s['name'][:45]:45} {s['horizon']:7} {s['status']:20} {s['n']:>5} "
            f"{s['hit_rate']*100:>5.1f}% {s['mean_return_net']:>+9.5f} {t:>6} {p:>7} {ratio:>8} {reasons}"
        )


def print_segmentation(conn):
    """Per-hypothesis breakdown by regime/session -- pulled from event
    context_json, joined against the same outcomes used above."""
    print("\nSegmentation by regime / session (1h horizon only, for brevity)")
    print("-" * 60)
    for h in store.active_hypotheses(conn):
        outcomes = store.outcomes_for_hypothesis(conn, h.id, "1h")
        if len(outcomes) < 5:
            continue
        buckets = defaultdict(list)
        for o in outcomes:
            ctx = json.loads(o["context_json"]) if o["context_json"] else {}
            key = (ctx.get("regime_label", "unknown"), ctx.get("session", "unknown"))
            buckets[key].append(o)

        printed_header = False
        for (regime, session), group in buckets.items():
            if len(group) < 5:
                continue
            if not printed_header:
                print(f"\n{h.name}")
                printed_header = True
            gross = np.array([o["forward_return"] for o in group])
            hits = np.array([bool(o["hit"]) for o in group])
            net = np.array([o["net_return"] for o in group])
            ev = evaluate_evidence(gross, hits, net)
            print(f"  regime={regime:10} session={session:8} n={ev['n']:>4} "
                  f"hit={ev['hit_rate']*100:.0f}% net={ev['mean_return_net']:+.5f} status={ev['status']}")


def main():
    with store.connect() as conn:
        print_leaderboard(conn)
        print_segmentation(conn)


if __name__ == "__main__":
    main()
