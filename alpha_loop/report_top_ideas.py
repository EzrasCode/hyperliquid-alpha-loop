"""
Ranked leaderboard of hypotheses by statistical significance -- the human
review surface. Nothing here recommends live trading; it just tells you
which hypotheses have (a) enough samples and (b) a t-stat worth a second
look, so you can decide whether to dig in further.

Usage: python -m alpha_loop.report_top_ideas
"""

import numpy as np

from . import store
from .backtest_engine import summarize_outcomes
from .hypothesis_bank import HORIZONS_MINUTES

MIN_SAMPLES_TO_RANK = 20


def main():
    rows = []
    with store.connect() as conn:
        for h in store.active_hypotheses(conn):
            for horizon in HORIZONS_MINUTES:
                outcomes = store.outcomes_for_hypothesis(conn, h.id, horizon)
                if not outcomes:
                    continue
                returns = np.array([o["forward_return"] for o in outcomes])
                hits = np.array([bool(o["hit"]) for o in outcomes])
                stats = summarize_outcomes(returns, hits)
                rows.append((h.name, h.source, horizon, stats))

    if not rows:
        print("No resolved outcomes yet. Let `python -m alpha_loop.loop` run for a while first.")
        return

    ranked = sorted(rows, key=lambda r: (r[3]["n"] >= MIN_SAMPLES_TO_RANK, abs(r[3]["t_stat"] or 0)), reverse=True)

    header = f"{'hypothesis':45} {'src':10} {'horizon':7} {'n':>5} {'hit%':>6} {'mean_ret':>9} {'t':>6} {'fee_adj_t':>10}"
    print(header)
    print("-" * len(header))
    for name, source, horizon, s in ranked:
        flag = "" if s["n"] >= MIN_SAMPLES_TO_RANK else "  (low n)"
        print(
            f"{name[:45]:45} {source:10} {horizon:7} {s['n']:>5} "
            f"{s['hit_rate']*100:>5.1f}% {s['mean_return']:>+9.4f} "
            f"{s['t_stat']:>6.2f} {s['t_stat_fee_adjusted']:>10.2f}{flag}"
        )


if __name__ == "__main__":
    main()
