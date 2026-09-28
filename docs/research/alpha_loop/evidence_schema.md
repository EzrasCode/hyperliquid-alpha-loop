# Evidence schema

Date: 2026-09-28

This documents what every (hypothesis, horizon) evidence row actually means,
and the gates that decide whether it's labeled `meets_all_gates`,
`insufficient_evidence`, or `insufficient_n`. This upgrade exists because the
loop's early output reported things like `n=1, hit_rate=1.00` as if that were
a finding -- it isn't. Nothing here is a claim that a signal works; it's a
claim that a signal has, or hasn't, cleared a stated bar of evidence so far.

## Where this comes from

- `backtest_engine.evaluate_evidence()` computes the whole block below from
  the raw resolved outcomes for one (hypothesis, horizon) pair.
- `reporting.build_cycle_report()` assembles that plus the research-loop
  transparency fields into one JSON object per cycle, appended to
  `cycle_reports.jsonl` (one line per cycle, never rewritten).
- `report_top_ideas.py` and the Discord message are both just renderings of
  the same underlying evidence, at different levels of detail.

## Per-hypothesis-per-horizon fields

**Sample & central tendency**: `n`, `mean_return_gross`, `median_return`,
`std_return`.

**Significance**: `t_stat` (None below n=2, `t_stat_status` says why),
`p_value` (normal approximation to the two-sided t-test -- documented as an
approximation, not exact, and only trusted once n is at or above
`MIN_N_FOR_SIGNIFICANCE`), `bootstrap_p` (block-bootstrap, block size
`BOOTSTRAP_BLOCK_SIZE`, to respect short-range autocorrelation rather than
treating each event as fully independent).

**Win/loss shape**: `hit_rate` plus a Wilson-interval `hit_rate_ci_low/high`
(much better-behaved than a normal-approximation CI at small n), `avg_win`,
`avg_loss`, `profit_factor`, `sharpe_per_trade` (per-event, not
annualized -- there's no fixed trade frequency to annualize against),
`max_drawdown` of the additive (non-compounding) cumulative-return curve.

**Execution realism**: `mean_return_net` = gross minus
`taker_fee_bps`/`slippage_bps` (both explicit constants in `config.py`, not
measured from real fills -- none exist yet). `fill_assumption`: entry price
is the price captured in the *same* data-fetch cycle the signal fired in
(never a later price), so there is no lookahead in entry price; the only
approximation is that a real order might not fill at exactly that mid/last
price.

**Forward path**: `mfe_mean`/`mae_mean` -- max favorable/adverse excursion
over the loop's own accumulated price snapshots between event time and the
horizon target, and `mfe_mae_ratio`. There is no stop-loss/take-profit rule
anywhere in this loop (it measures signals, not a full trading strategy), so
`hit_stop`/`hit_target` fields from a typical execution log don't apply here
and aren't fabricated.

**Sub-period robustness**: `sign_consistent_subperiods` -- true only if the
sign of the mean return holds across at least 2 of 3 chronological
sub-periods, so a result that's only positive because of one early lucky
stretch doesn't pass.

## Event context (per fired event, not per aggregate)

`session` (Asia/London/NY/Late, by UTC hour), `regime_label`
(`trending`/`ranging`/`insufficient_history` -- a simple trend-strength
heuristic against the loop's own accumulated volatility history, not a real
regime model), `vol_percentile` (this event's realized vol vs. the
distribution of same-length historical windows the loop has itself
observed -- `None` until at least `MIN_HISTORY_WINDOWS_FOR_PERCENTILE`
windows exist), `funding_rate`, `tick_count`, `data_latency_ms`,
`trigger_value`/`trigger_threshold`/`trigger_zscore` (what specifically
crossed what cutoff).

Regime/session/vol-percentile context genuinely only becomes meaningful
after days of accumulated history -- see `market_context.py`'s docstring.
Segmentation by these fields (`report_top_ideas.py`'s second table) exists
so a signal that only works in one regime doesn't get buried in an aggregate
average.

## Gating

A row is `insufficient_n` below `MIN_N_FOR_SIGNIFICANCE` (30), full stop --
none of the other gates are even worth checking yet -- **unless** it also
clears a softer watch-list bar (`n >= MIN_N_FOR_WATCHLIST` (5),
`|t| >= WATCHLIST_MIN_ABS_T` (1.0), positive net return, hit rate > 50%), in
which case it's `insufficient_n_but_promising` instead. This exists so an
early signal that's trending real doesn't get buried in the same bucket as
one that's already flat -- it is still not a claim the signal works, only
that it's worth watching as more samples accumulate. Above n=30, it's
`meets_all_gates` only if ALL of: `|t_stat| >= MIN_ABS_T_STAT`,
`mean_return_net > 0`, `mfe_mae_ratio > MIN_MFE_MAE_RATIO`,
`bootstrap_p < MAX_BOOTSTRAP_P`, and `sign_consistent_subperiods`. Otherwise
`insufficient_evidence`, with the specific failed gates listed in
`gate_failure_reasons`. `meets_all_gates` is not a claim the signal works --
it means it has cleared the stated bar of evidence so far and is worth a
closer, human look before anything is built into an actual strategy.

## Research-loop transparency (per cycle, not per hypothesis)

`hypotheses_generated` (raw count the LLM returned), `hypotheses_promoted`
(how many were both valid and new), `hypotheses_rejected` (each with a
`reason`), `why_no_new_leads` (explicit reason when the count is zero --
"OPENROUTER_API_KEY not set", "model returned zero candidates", "all
proposed items failed validation", "all accepted candidates were duplicates
of existing hypotheses" -- rather than a silent zero), `new_research_leads`
(arXiv papers), `compute_budget_used` (hypotheses evaluated, outcomes
resolved this cycle), `data_window` (start/end of this cycle's data pull).
