# Alpha loop decision log

Append-only. One entry per cycle that changed the hypothesis bank or moved a hypothesis's stats meaningfully. See alpha_loop_overview_20260927.md for methodology.

## 2026-09-28 02:35 UTC

cycle 1: 2 events fired, 0 new hypotheses added
no resolved outcomes yet

## 2026-09-28 03:21 UTC

cycle 2: 2 events fired, 0 new hypotheses added, 0 new research leads
Liquidation cascade momentum (5m concentration) [5m]: n=1 hit_rate=1.00 mean_return=+0.0002 t=nan
Liquidation cascade momentum (5m concentration) [15m]: n=1 hit_rate=1.00 mean_return=+0.0002 t=nan
CVD / price divergence (BTC, 1h ticks) [5m]: n=1 hit_rate=0.00 mean_return=-0.0002 t=nan
CVD / price divergence (BTC, 1h ticks) [15m]: n=1 hit_rate=0.00 mean_return=-0.0002 t=nan

## 2026-09-28: evidence schema upgrade

The two entries above are a perfect example of the problem this fixes: an
`n=1, hit_rate=1.00, t=nan` line printed with no indication that it means
nothing. From this point on, every outcome is gated by sample size and
several other evidence checks before being called anything other than
"insufficient_n" -- see docs/research/alpha_loop/evidence_schema.md for the
full schema. `alpha_loop.db` was reset to pick up new columns (event
context, trigger fields, net return, MFE/MAE) that the old schema didn't
have; nothing of real value was lost (the two entries above were still
single-sample noise). Going forward, this file stays a short human-readable
summary per cycle; the full structured record (every field in the schema
doc, one JSON object per cycle) lives in `cycle_reports.jsonl`, never
rewritten.

## 2026-09-28 04:36 UTC

cycle 1 -- events_fired=0 hyp_generated=0 hyp_promoted=0 new_research_leads=0
no resolved outcomes yet

## 2026-09-28 09:49 UTC

cycle 2 -- events_fired=1 hyp_generated=0 hyp_promoted=0 new_research_leads=0
no resolved outcomes yet

## 2026-09-28 17:52 UTC

cycle 3 -- events_fired=1 hyp_generated=0 hyp_promoted=0 new_research_leads=0
· CVD / price divergence (BTC, 1h ticks)     [ 5m] n=1    status=insufficient_n       hit=100% net=+0.01349
· CVD / price divergence (BTC, 1h ticks)     [15m] n=1    status=insufficient_n       hit=100% net=+0.01349
· CVD / price divergence (BTC, 1h ticks)     [ 1h] n=1    status=insufficient_n       hit=100% net=+0.01349
· CVD / price divergence (BTC, 1h ticks)     [ 4h] n=1    status=insufficient_n       hit=100% net=+0.01349

## 2026-09-28 22:59 UTC

cycle 4 -- events_fired=0 hyp_generated=0 hyp_promoted=0 new_research_leads=0
· CVD / price divergence (BTC, 1h ticks)     [ 5m] n=2    status=insufficient_n       hit=100% net=+0.00865
· CVD / price divergence (BTC, 1h ticks)     [15m] n=2    status=insufficient_n       hit=100% net=+0.00865
· CVD / price divergence (BTC, 1h ticks)     [ 1h] n=2    status=insufficient_n       hit=100% net=+0.00865
· CVD / price divergence (BTC, 1h ticks)     [ 4h] n=2    status=insufficient_n       hit=100% net=+0.00865

## 2026-09-29 02:33 UTC

cycle 5 -- events_fired=0 hyp_generated=0 hyp_promoted=0 new_research_leads=0
· CVD / price divergence (BTC, 1h ticks)     [ 5m] n=2    status=insufficient_n       hit=100% net=+0.00865
· CVD / price divergence (BTC, 1h ticks)     [15m] n=2    status=insufficient_n       hit=100% net=+0.00865
· CVD / price divergence (BTC, 1h ticks)     [ 1h] n=2    status=insufficient_n       hit=100% net=+0.00865
· CVD / price divergence (BTC, 1h ticks)     [ 4h] n=2    status=insufficient_n       hit=100% net=+0.00865

## 2026-09-29 09:01 UTC

cycle 6 -- events_fired=1 hyp_generated=0 hyp_promoted=0 new_research_leads=0
· CVD / price divergence (BTC, 1h ticks)     [ 5m] n=2    status=insufficient_n       hit=100% net=+0.00865
· CVD / price divergence (BTC, 1h ticks)     [15m] n=2    status=insufficient_n       hit=100% net=+0.00865
· CVD / price divergence (BTC, 1h ticks)     [ 1h] n=2    status=insufficient_n       hit=100% net=+0.00865
· CVD / price divergence (BTC, 1h ticks)     [ 4h] n=2    status=insufficient_n       hit=100% net=+0.00865

## 2026-09-29 15:43 UTC

cycle 7 -- events_fired=1 hyp_generated=0 hyp_promoted=0 new_research_leads=0
· CVD / price divergence (BTC, 1h ticks)     [ 5m] n=3    status=insufficient_n       hit= 67% net=+0.00255
· CVD / price divergence (BTC, 1h ticks)     [15m] n=3    status=insufficient_n       hit= 67% net=+0.00255
· CVD / price divergence (BTC, 1h ticks)     [ 1h] n=3    status=insufficient_n       hit= 67% net=+0.00255
· CVD / price divergence (BTC, 1h ticks)     [ 4h] n=3    status=insufficient_n       hit= 67% net=+0.00255

## 2026-09-29 20:15 UTC

cycle 8 -- events_fired=0 hyp_generated=0 hyp_promoted=0 new_research_leads=0
· CVD / price divergence (BTC, 1h ticks)     [ 5m] n=4    status=insufficient_n       hit= 75% net=+0.00280
· CVD / price divergence (BTC, 1h ticks)     [15m] n=4    status=insufficient_n       hit= 75% net=+0.00280
· CVD / price divergence (BTC, 1h ticks)     [ 1h] n=4    status=insufficient_n       hit= 75% net=+0.00280
· CVD / price divergence (BTC, 1h ticks)     [ 4h] n=4    status=insufficient_n       hit= 75% net=+0.00280

## 2026-09-29 23:47 UTC

cycle 9 -- events_fired=0 hyp_generated=0 hyp_promoted=0 new_research_leads=0
· CVD / price divergence (BTC, 1h ticks)     [ 5m] n=4    status=insufficient_n       hit= 75% net=+0.00280
· CVD / price divergence (BTC, 1h ticks)     [15m] n=4    status=insufficient_n       hit= 75% net=+0.00280
· CVD / price divergence (BTC, 1h ticks)     [ 1h] n=4    status=insufficient_n       hit= 75% net=+0.00280
· CVD / price divergence (BTC, 1h ticks)     [ 4h] n=4    status=insufficient_n       hit= 75% net=+0.00280

## 2026-09-30 02:34 UTC

cycle 10 -- events_fired=0 hyp_generated=0 hyp_promoted=0 new_research_leads=0
· CVD / price divergence (BTC, 1h ticks)     [ 5m] n=4    status=insufficient_n       hit= 75% net=+0.00280
· CVD / price divergence (BTC, 1h ticks)     [15m] n=4    status=insufficient_n       hit= 75% net=+0.00280
· CVD / price divergence (BTC, 1h ticks)     [ 1h] n=4    status=insufficient_n       hit= 75% net=+0.00280
· CVD / price divergence (BTC, 1h ticks)     [ 4h] n=4    status=insufficient_n       hit= 75% net=+0.00280

## 2026-09-30 09:00 UTC

cycle 11 -- events_fired=1 hyp_generated=0 hyp_promoted=0 new_research_leads=0
· CVD / price divergence (BTC, 1h ticks)     [ 5m] n=4    status=insufficient_n       hit= 75% net=+0.00280
· CVD / price divergence (BTC, 1h ticks)     [15m] n=4    status=insufficient_n       hit= 75% net=+0.00280
· CVD / price divergence (BTC, 1h ticks)     [ 1h] n=4    status=insufficient_n       hit= 75% net=+0.00280
· CVD / price divergence (BTC, 1h ticks)     [ 4h] n=4    status=insufficient_n       hit= 75% net=+0.00280

## 2026-09-30 15:53 UTC

cycle 12 -- events_fired=2 hyp_generated=0 hyp_promoted=0 new_research_leads=14
why_no_new_hypotheses: OpenRouter call failed: Error code: 401 - {'error': {'message': 'User not found.', 'code': 401}}
👀 CVD / price divergence (BTC, 1h ticks)     [ 5m] n=5    status=insufficient_n_but_promising hit= 80% net=+0.00491
👀 CVD / price divergence (BTC, 1h ticks)     [15m] n=5    status=insufficient_n_but_promising hit= 80% net=+0.00491
👀 CVD / price divergence (BTC, 1h ticks)     [ 1h] n=5    status=insufficient_n_but_promising hit= 80% net=+0.00491
👀 CVD / price divergence (BTC, 1h ticks)     [ 4h] n=5    status=insufficient_n_but_promising hit= 80% net=+0.00491

## 2026-09-30 20:35 UTC

cycle 13 -- events_fired=1 hyp_generated=0 hyp_promoted=0 new_research_leads=0
👀 CVD / price divergence (BTC, 1h ticks)     [ 5m] n=6    status=insufficient_n_but_promising hit= 83% net=+0.00500
👀 CVD / price divergence (BTC, 1h ticks)     [15m] n=6    status=insufficient_n_but_promising hit= 83% net=+0.00500
👀 CVD / price divergence (BTC, 1h ticks)     [ 1h] n=6    status=insufficient_n_but_promising hit= 83% net=+0.00500
👀 CVD / price divergence (BTC, 1h ticks)     [ 4h] n=6    status=insufficient_n_but_promising hit= 83% net=+0.00500
· Liquidation cascade momentum (5m concentra [ 5m] n=1    status=insufficient_n       hit=  0% net=-0.00808
· Liquidation cascade momentum (5m concentra [15m] n=1    status=insufficient_n       hit=  0% net=-0.00808
· Liquidation cascade momentum (5m concentra [ 1h] n=1    status=insufficient_n       hit=  0% net=-0.00808
· Liquidation cascade momentum (5m concentra [ 4h] n=1    status=insufficient_n       hit=  0% net=-0.00808

## 2026-10-01 00:10 UTC

cycle 14 -- events_fired=1 hyp_generated=0 hyp_promoted=0 new_research_leads=0
👀 CVD / price divergence (BTC, 1h ticks)     [ 5m] n=7    status=insufficient_n_but_promising hit= 71% net=+0.00372
👀 CVD / price divergence (BTC, 1h ticks)     [15m] n=7    status=insufficient_n_but_promising hit= 71% net=+0.00372
👀 CVD / price divergence (BTC, 1h ticks)     [ 1h] n=7    status=insufficient_n_but_promising hit= 71% net=+0.00372
👀 CVD / price divergence (BTC, 1h ticks)     [ 4h] n=6    status=insufficient_n_but_promising hit= 83% net=+0.00500
· Liquidation cascade momentum (5m concentra [ 5m] n=1    status=insufficient_n       hit=  0% net=-0.00808
· Liquidation cascade momentum (5m concentra [15m] n=1    status=insufficient_n       hit=  0% net=-0.00808
· Liquidation cascade momentum (5m concentra [ 1h] n=1    status=insufficient_n       hit=  0% net=-0.00808
· Liquidation cascade momentum (5m concentra [ 4h] n=1    status=insufficient_n       hit=  0% net=-0.00808

## 2026-10-01 06:02 UTC

cycle 15 -- events_fired=2 hyp_generated=0 hyp_promoted=0 new_research_leads=0
👀 CVD / price divergence (BTC, 1h ticks)     [ 5m] n=8    status=insufficient_n_but_promising hit= 75% net=+0.00431
👀 CVD / price divergence (BTC, 1h ticks)     [15m] n=8    status=insufficient_n_but_promising hit= 75% net=+0.00431
👀 CVD / price divergence (BTC, 1h ticks)     [ 1h] n=8    status=insufficient_n_but_promising hit= 75% net=+0.00431
👀 CVD / price divergence (BTC, 1h ticks)     [ 4h] n=8    status=insufficient_n_but_promising hit= 88% net=+0.00551
· Liquidation cascade momentum (5m concentra [ 5m] n=1    status=insufficient_n       hit=  0% net=-0.00808
· Liquidation cascade momentum (5m concentra [15m] n=1    status=insufficient_n       hit=  0% net=-0.00808
· Liquidation cascade momentum (5m concentra [ 1h] n=1    status=insufficient_n       hit=  0% net=-0.00808
· Liquidation cascade momentum (5m concentra [ 4h] n=1    status=insufficient_n       hit=  0% net=-0.00808

## 2026-10-01 13:04 UTC

cycle 16 -- events_fired=2 hyp_generated=0 hyp_promoted=0 new_research_leads=0
👀 CVD / price divergence (BTC, 1h ticks)     [ 5m] n=9    status=insufficient_n_but_promising hit= 78% net=+0.00453
👀 CVD / price divergence (BTC, 1h ticks)     [15m] n=9    status=insufficient_n_but_promising hit= 78% net=+0.00453
👀 CVD / price divergence (BTC, 1h ticks)     [ 1h] n=9    status=insufficient_n_but_promising hit= 78% net=+0.00453
👀 CVD / price divergence (BTC, 1h ticks)     [ 4h] n=9    status=insufficient_n_but_promising hit= 89% net=+0.00560
· Liquidation cascade momentum (5m concentra [ 5m] n=2    status=insufficient_n       hit=  0% net=-0.00849
· Liquidation cascade momentum (5m concentra [15m] n=2    status=insufficient_n       hit=  0% net=-0.00849
· Liquidation cascade momentum (5m concentra [ 1h] n=2    status=insufficient_n       hit=  0% net=-0.00849
· Liquidation cascade momentum (5m concentra [ 4h] n=2    status=insufficient_n       hit=  0% net=-0.00849

## 2026-10-01 18:51 UTC

cycle 17 -- events_fired=0 hyp_generated=0 hyp_promoted=0 new_research_leads=0
👀 CVD / price divergence (BTC, 1h ticks)     [ 5m] n=10   status=insufficient_n_but_promising hit= 80% net=+0.00524
👀 CVD / price divergence (BTC, 1h ticks)     [15m] n=10   status=insufficient_n_but_promising hit= 80% net=+0.00524
👀 CVD / price divergence (BTC, 1h ticks)     [ 1h] n=10   status=insufficient_n_but_promising hit= 80% net=+0.00524
👀 CVD / price divergence (BTC, 1h ticks)     [ 4h] n=10   status=insufficient_n_but_promising hit= 90% net=+0.00621
· Liquidation cascade momentum (5m concentra [ 5m] n=3    status=insufficient_n       hit=  0% net=-0.01042
· Liquidation cascade momentum (5m concentra [15m] n=3    status=insufficient_n       hit=  0% net=-0.01042
· Liquidation cascade momentum (5m concentra [ 1h] n=3    status=insufficient_n       hit=  0% net=-0.01042
· Liquidation cascade momentum (5m concentra [ 4h] n=3    status=insufficient_n       hit=  0% net=-0.01042

## 2026-10-01 22:59 UTC

cycle 18 -- events_fired=0 hyp_generated=0 hyp_promoted=0 new_research_leads=0
👀 CVD / price divergence (BTC, 1h ticks)     [ 5m] n=10   status=insufficient_n_but_promising hit= 80% net=+0.00524
👀 CVD / price divergence (BTC, 1h ticks)     [15m] n=10   status=insufficient_n_but_promising hit= 80% net=+0.00524
👀 CVD / price divergence (BTC, 1h ticks)     [ 1h] n=10   status=insufficient_n_but_promising hit= 80% net=+0.00524
👀 CVD / price divergence (BTC, 1h ticks)     [ 4h] n=10   status=insufficient_n_but_promising hit= 90% net=+0.00621
· Liquidation cascade momentum (5m concentra [ 5m] n=3    status=insufficient_n       hit=  0% net=-0.01042
· Liquidation cascade momentum (5m concentra [15m] n=3    status=insufficient_n       hit=  0% net=-0.01042
· Liquidation cascade momentum (5m concentra [ 1h] n=3    status=insufficient_n       hit=  0% net=-0.01042
· Liquidation cascade momentum (5m concentra [ 4h] n=3    status=insufficient_n       hit=  0% net=-0.01042

## 2026-10-02 02:09 UTC

cycle 19 -- events_fired=2 hyp_generated=0 hyp_promoted=0 new_research_leads=0
👀 CVD / price divergence (BTC, 1h ticks)     [ 5m] n=10   status=insufficient_n_but_promising hit= 80% net=+0.00524
👀 CVD / price divergence (BTC, 1h ticks)     [15m] n=10   status=insufficient_n_but_promising hit= 80% net=+0.00524
👀 CVD / price divergence (BTC, 1h ticks)     [ 1h] n=10   status=insufficient_n_but_promising hit= 80% net=+0.00524
👀 CVD / price divergence (BTC, 1h ticks)     [ 4h] n=10   status=insufficient_n_but_promising hit= 90% net=+0.00621
· Liquidation cascade momentum (5m concentra [ 5m] n=3    status=insufficient_n       hit=  0% net=-0.01042
· Liquidation cascade momentum (5m concentra [15m] n=3    status=insufficient_n       hit=  0% net=-0.01042
· Liquidation cascade momentum (5m concentra [ 1h] n=3    status=insufficient_n       hit=  0% net=-0.01042
· Liquidation cascade momentum (5m concentra [ 4h] n=3    status=insufficient_n       hit=  0% net=-0.01042

## 2026-10-02 08:34 UTC

cycle 20 -- events_fired=1 hyp_generated=0 hyp_promoted=0 new_research_leads=0
👀 CVD / price divergence (BTC, 1h ticks)     [ 5m] n=11   status=insufficient_n_but_promising hit= 73% net=+0.00335
👀 CVD / price divergence (BTC, 1h ticks)     [15m] n=11   status=insufficient_n_but_promising hit= 73% net=+0.00335
👀 CVD / price divergence (BTC, 1h ticks)     [ 1h] n=11   status=insufficient_n_but_promising hit= 73% net=+0.00335
👀 CVD / price divergence (BTC, 1h ticks)     [ 4h] n=11   status=insufficient_n_but_promising hit= 82% net=+0.00423
· Liquidation cascade momentum (5m concentra [ 5m] n=4    status=insufficient_n       hit= 25% net=-0.00457
· Liquidation cascade momentum (5m concentra [15m] n=4    status=insufficient_n       hit= 25% net=-0.00457
· Liquidation cascade momentum (5m concentra [ 1h] n=4    status=insufficient_n       hit= 25% net=-0.00457
· Liquidation cascade momentum (5m concentra [ 4h] n=4    status=insufficient_n       hit= 25% net=-0.00457

## 2026-10-02 14:59 UTC

cycle 21 -- events_fired=2 hyp_generated=0 hyp_promoted=0 new_research_leads=0
👀 CVD / price divergence (BTC, 1h ticks)     [ 5m] n=12   status=insufficient_n_but_promising hit= 75% net=+0.00354
👀 CVD / price divergence (BTC, 1h ticks)     [15m] n=12   status=insufficient_n_but_promising hit= 75% net=+0.00354
👀 CVD / price divergence (BTC, 1h ticks)     [ 1h] n=12   status=insufficient_n_but_promising hit= 75% net=+0.00354
👀 CVD / price divergence (BTC, 1h ticks)     [ 4h] n=12   status=insufficient_n_but_promising hit= 83% net=+0.00434
· Liquidation cascade momentum (5m concentra [ 5m] n=4    status=insufficient_n       hit= 25% net=-0.00457
· Liquidation cascade momentum (5m concentra [15m] n=4    status=insufficient_n       hit= 25% net=-0.00457
· Liquidation cascade momentum (5m concentra [ 1h] n=4    status=insufficient_n       hit= 25% net=-0.00457
· Liquidation cascade momentum (5m concentra [ 4h] n=4    status=insufficient_n       hit= 25% net=-0.00457

## 2026-10-02 19:53 UTC

cycle 22 -- events_fired=0 hyp_generated=0 hyp_promoted=0 new_research_leads=0
👀 CVD / price divergence (BTC, 1h ticks)     [ 5m] n=13   status=insufficient_n_but_promising hit= 69% net=+0.00184
👀 CVD / price divergence (BTC, 1h ticks)     [15m] n=13   status=insufficient_n_but_promising hit= 69% net=+0.00184
👀 CVD / price divergence (BTC, 1h ticks)     [ 1h] n=13   status=insufficient_n_but_promising hit= 69% net=+0.00184
👀 CVD / price divergence (BTC, 1h ticks)     [ 4h] n=13   status=insufficient_n_but_promising hit= 77% net=+0.00258
· Liquidation cascade momentum (5m concentra [ 5m] n=5    status=insufficient_n       hit= 40% net=-0.00047
· Liquidation cascade momentum (5m concentra [15m] n=5    status=insufficient_n       hit= 40% net=-0.00047
· Liquidation cascade momentum (5m concentra [ 1h] n=5    status=insufficient_n       hit= 40% net=-0.00047
· Liquidation cascade momentum (5m concentra [ 4h] n=5    status=insufficient_n       hit= 40% net=-0.00047

## 2026-10-02 23:36 UTC

cycle 23 -- events_fired=0 hyp_generated=0 hyp_promoted=0 new_research_leads=0
👀 CVD / price divergence (BTC, 1h ticks)     [ 5m] n=13   status=insufficient_n_but_promising hit= 69% net=+0.00184
👀 CVD / price divergence (BTC, 1h ticks)     [15m] n=13   status=insufficient_n_but_promising hit= 69% net=+0.00184
👀 CVD / price divergence (BTC, 1h ticks)     [ 1h] n=13   status=insufficient_n_but_promising hit= 69% net=+0.00184
👀 CVD / price divergence (BTC, 1h ticks)     [ 4h] n=13   status=insufficient_n_but_promising hit= 77% net=+0.00258
· Liquidation cascade momentum (5m concentra [ 5m] n=5    status=insufficient_n       hit= 40% net=-0.00047
· Liquidation cascade momentum (5m concentra [15m] n=5    status=insufficient_n       hit= 40% net=-0.00047
· Liquidation cascade momentum (5m concentra [ 1h] n=5    status=insufficient_n       hit= 40% net=-0.00047
· Liquidation cascade momentum (5m concentra [ 4h] n=5    status=insufficient_n       hit= 40% net=-0.00047

## 2026-10-03 02:19 UTC

cycle 24 -- events_fired=1 hyp_generated=0 hyp_promoted=0 new_research_leads=6
why_no_new_hypotheses: OpenRouter call failed: Error code: 401 - {'error': {'message': 'User not found.', 'code': 401}}
👀 CVD / price divergence (BTC, 1h ticks)     [ 5m] n=13   status=insufficient_n_but_promising hit= 69% net=+0.00184
👀 CVD / price divergence (BTC, 1h ticks)     [15m] n=13   status=insufficient_n_but_promising hit= 69% net=+0.00184
👀 CVD / price divergence (BTC, 1h ticks)     [ 1h] n=13   status=insufficient_n_but_promising hit= 69% net=+0.00184
👀 CVD / price divergence (BTC, 1h ticks)     [ 4h] n=13   status=insufficient_n_but_promising hit= 77% net=+0.00258
· Liquidation cascade momentum (5m concentra [ 5m] n=5    status=insufficient_n       hit= 40% net=-0.00047
· Liquidation cascade momentum (5m concentra [15m] n=5    status=insufficient_n       hit= 40% net=-0.00047
· Liquidation cascade momentum (5m concentra [ 1h] n=5    status=insufficient_n       hit= 40% net=-0.00047
· Liquidation cascade momentum (5m concentra [ 4h] n=5    status=insufficient_n       hit= 40% net=-0.00047

## 2026-10-03 08:22 UTC

cycle 25 -- events_fired=0 hyp_generated=0 hyp_promoted=0 new_research_leads=0
👀 CVD / price divergence (BTC, 1h ticks)     [ 5m] n=14   status=insufficient_n_but_promising hit= 64% net=+0.00155
👀 CVD / price divergence (BTC, 1h ticks)     [15m] n=14   status=insufficient_n_but_promising hit= 64% net=+0.00155
👀 CVD / price divergence (BTC, 1h ticks)     [ 1h] n=14   status=insufficient_n_but_promising hit= 64% net=+0.00155
👀 CVD / price divergence (BTC, 1h ticks)     [ 4h] n=14   status=insufficient_n_but_promising hit= 71% net=+0.00224
· Liquidation cascade momentum (5m concentra [ 5m] n=5    status=insufficient_n       hit= 40% net=-0.00047
· Liquidation cascade momentum (5m concentra [15m] n=5    status=insufficient_n       hit= 40% net=-0.00047
· Liquidation cascade momentum (5m concentra [ 1h] n=5    status=insufficient_n       hit= 40% net=-0.00047
· Liquidation cascade momentum (5m concentra [ 4h] n=5    status=insufficient_n       hit= 40% net=-0.00047

## 2026-10-03 13:36 UTC

cycle 26 -- events_fired=0 hyp_generated=0 hyp_promoted=0 new_research_leads=0
👀 CVD / price divergence (BTC, 1h ticks)     [ 5m] n=14   status=insufficient_n_but_promising hit= 64% net=+0.00155
👀 CVD / price divergence (BTC, 1h ticks)     [15m] n=14   status=insufficient_n_but_promising hit= 64% net=+0.00155
👀 CVD / price divergence (BTC, 1h ticks)     [ 1h] n=14   status=insufficient_n_but_promising hit= 64% net=+0.00155
👀 CVD / price divergence (BTC, 1h ticks)     [ 4h] n=14   status=insufficient_n_but_promising hit= 71% net=+0.00224
· Liquidation cascade momentum (5m concentra [ 5m] n=5    status=insufficient_n       hit= 40% net=-0.00047
· Liquidation cascade momentum (5m concentra [15m] n=5    status=insufficient_n       hit= 40% net=-0.00047
· Liquidation cascade momentum (5m concentra [ 1h] n=5    status=insufficient_n       hit= 40% net=-0.00047
· Liquidation cascade momentum (5m concentra [ 4h] n=5    status=insufficient_n       hit= 40% net=-0.00047

## 2026-10-03 17:37 UTC

cycle 27 -- events_fired=0 hyp_generated=0 hyp_promoted=0 new_research_leads=0
👀 CVD / price divergence (BTC, 1h ticks)     [ 5m] n=14   status=insufficient_n_but_promising hit= 64% net=+0.00155
👀 CVD / price divergence (BTC, 1h ticks)     [15m] n=14   status=insufficient_n_but_promising hit= 64% net=+0.00155
👀 CVD / price divergence (BTC, 1h ticks)     [ 1h] n=14   status=insufficient_n_but_promising hit= 64% net=+0.00155
👀 CVD / price divergence (BTC, 1h ticks)     [ 4h] n=14   status=insufficient_n_but_promising hit= 71% net=+0.00224
· Liquidation cascade momentum (5m concentra [ 5m] n=5    status=insufficient_n       hit= 40% net=-0.00047
· Liquidation cascade momentum (5m concentra [15m] n=5    status=insufficient_n       hit= 40% net=-0.00047
· Liquidation cascade momentum (5m concentra [ 1h] n=5    status=insufficient_n       hit= 40% net=-0.00047
· Liquidation cascade momentum (5m concentra [ 4h] n=5    status=insufficient_n       hit= 40% net=-0.00047

## 2026-10-03 20:12 UTC

cycle 28 -- events_fired=1 hyp_generated=0 hyp_promoted=0 new_research_leads=0
👀 CVD / price divergence (BTC, 1h ticks)     [ 5m] n=14   status=insufficient_n_but_promising hit= 64% net=+0.00155
👀 CVD / price divergence (BTC, 1h ticks)     [15m] n=14   status=insufficient_n_but_promising hit= 64% net=+0.00155
👀 CVD / price divergence (BTC, 1h ticks)     [ 1h] n=14   status=insufficient_n_but_promising hit= 64% net=+0.00155
👀 CVD / price divergence (BTC, 1h ticks)     [ 4h] n=14   status=insufficient_n_but_promising hit= 71% net=+0.00224
· Liquidation cascade momentum (5m concentra [ 5m] n=5    status=insufficient_n       hit= 40% net=-0.00047
· Liquidation cascade momentum (5m concentra [15m] n=5    status=insufficient_n       hit= 40% net=-0.00047
· Liquidation cascade momentum (5m concentra [ 1h] n=5    status=insufficient_n       hit= 40% net=-0.00047
· Liquidation cascade momentum (5m concentra [ 4h] n=5    status=insufficient_n       hit= 40% net=-0.00047

## 2026-10-03 23:09 UTC

cycle 29 -- events_fired=0 hyp_generated=0 hyp_promoted=0 new_research_leads=0
👀 CVD / price divergence (BTC, 1h ticks)     [ 5m] n=14   status=insufficient_n_but_promising hit= 64% net=+0.00155
👀 CVD / price divergence (BTC, 1h ticks)     [15m] n=14   status=insufficient_n_but_promising hit= 64% net=+0.00155
👀 CVD / price divergence (BTC, 1h ticks)     [ 1h] n=14   status=insufficient_n_but_promising hit= 64% net=+0.00155
👀 CVD / price divergence (BTC, 1h ticks)     [ 4h] n=14   status=insufficient_n_but_promising hit= 71% net=+0.00224
· Liquidation cascade momentum (5m concentra [ 5m] n=5    status=insufficient_n       hit= 40% net=-0.00047
· Liquidation cascade momentum (5m concentra [15m] n=5    status=insufficient_n       hit= 40% net=-0.00047
· Liquidation cascade momentum (5m concentra [ 1h] n=5    status=insufficient_n       hit= 40% net=-0.00047
· Liquidation cascade momentum (5m concentra [ 4h] n=5    status=insufficient_n       hit= 40% net=-0.00047
· HLP sentiment squeeze (z >= 2.0)           [ 5m] n=1    status=insufficient_n       hit=100% net=+0.00012
· HLP sentiment squeeze (z >= 2.0)           [15m] n=1    status=insufficient_n       hit=100% net=+0.00012
· HLP sentiment squeeze (z >= 2.0)           [ 1h] n=1    status=insufficient_n       hit=100% net=+0.00012

## 2026-10-04 02:41 UTC

cycle 30 -- events_fired=1 hyp_generated=0 hyp_promoted=0 new_research_leads=0
👀 CVD / price divergence (BTC, 1h ticks)     [ 5m] n=14   status=insufficient_n_but_promising hit= 64% net=+0.00155
👀 CVD / price divergence (BTC, 1h ticks)     [15m] n=14   status=insufficient_n_but_promising hit= 64% net=+0.00155
👀 CVD / price divergence (BTC, 1h ticks)     [ 1h] n=14   status=insufficient_n_but_promising hit= 64% net=+0.00155
👀 CVD / price divergence (BTC, 1h ticks)     [ 4h] n=14   status=insufficient_n_but_promising hit= 71% net=+0.00224
· Liquidation cascade momentum (5m concentra [ 5m] n=5    status=insufficient_n       hit= 40% net=-0.00047
· Liquidation cascade momentum (5m concentra [15m] n=5    status=insufficient_n       hit= 40% net=-0.00047
· Liquidation cascade momentum (5m concentra [ 1h] n=5    status=insufficient_n       hit= 40% net=-0.00047
· Liquidation cascade momentum (5m concentra [ 4h] n=5    status=insufficient_n       hit= 40% net=-0.00047
· HLP sentiment squeeze (z >= 2.0)           [ 5m] n=1    status=insufficient_n       hit=100% net=+0.00012
· HLP sentiment squeeze (z >= 2.0)           [15m] n=1    status=insufficient_n       hit=100% net=+0.00012
· HLP sentiment squeeze (z >= 2.0)           [ 1h] n=1    status=insufficient_n       hit=100% net=+0.00012
· HLP sentiment squeeze (z >= 2.0)           [ 4h] n=1    status=insufficient_n       hit=100% net=-0.00049

## 2026-10-04 08:50 UTC

cycle 31 -- events_fired=1 hyp_generated=0 hyp_promoted=0 new_research_leads=0
👀 CVD / price divergence (BTC, 1h ticks)     [ 4h] n=15   status=insufficient_n_but_promising hit= 67% net=+0.00175
· CVD / price divergence (BTC, 1h ticks)     [ 5m] n=15   status=insufficient_n       hit= 60% net=+0.00110
· CVD / price divergence (BTC, 1h ticks)     [15m] n=15   status=insufficient_n       hit= 60% net=+0.00110
· CVD / price divergence (BTC, 1h ticks)     [ 1h] n=15   status=insufficient_n       hit= 60% net=+0.00110
· Liquidation cascade momentum (5m concentra [ 5m] n=5    status=insufficient_n       hit= 40% net=-0.00047
· Liquidation cascade momentum (5m concentra [15m] n=5    status=insufficient_n       hit= 40% net=-0.00047
· Liquidation cascade momentum (5m concentra [ 1h] n=5    status=insufficient_n       hit= 40% net=-0.00047
· Liquidation cascade momentum (5m concentra [ 4h] n=5    status=insufficient_n       hit= 40% net=-0.00047
· HLP sentiment squeeze (z >= 2.0)           [ 5m] n=1    status=insufficient_n       hit=100% net=+0.00012
· HLP sentiment squeeze (z >= 2.0)           [15m] n=1    status=insufficient_n       hit=100% net=+0.00012
· HLP sentiment squeeze (z >= 2.0)           [ 1h] n=1    status=insufficient_n       hit=100% net=+0.00012
· HLP sentiment squeeze (z >= 2.0)           [ 4h] n=1    status=insufficient_n       hit=100% net=-0.00049

## 2026-10-04 14:34 UTC

cycle 32 -- events_fired=0 hyp_generated=0 hyp_promoted=0 new_research_leads=0
👀 CVD / price divergence (BTC, 1h ticks)     [ 4h] n=16   status=insufficient_n_but_promising hit= 62% net=+0.00151
· CVD / price divergence (BTC, 1h ticks)     [ 5m] n=16   status=insufficient_n       hit= 56% net=+0.00091
· CVD / price divergence (BTC, 1h ticks)     [15m] n=16   status=insufficient_n       hit= 56% net=+0.00091
· CVD / price divergence (BTC, 1h ticks)     [ 1h] n=16   status=insufficient_n       hit= 56% net=+0.00091
· Liquidation cascade momentum (5m concentra [ 5m] n=5    status=insufficient_n       hit= 40% net=-0.00047
· Liquidation cascade momentum (5m concentra [15m] n=5    status=insufficient_n       hit= 40% net=-0.00047
· Liquidation cascade momentum (5m concentra [ 1h] n=5    status=insufficient_n       hit= 40% net=-0.00047
· Liquidation cascade momentum (5m concentra [ 4h] n=5    status=insufficient_n       hit= 40% net=-0.00047
· HLP sentiment squeeze (z >= 2.0)           [ 5m] n=1    status=insufficient_n       hit=100% net=+0.00012
· HLP sentiment squeeze (z >= 2.0)           [15m] n=1    status=insufficient_n       hit=100% net=+0.00012
· HLP sentiment squeeze (z >= 2.0)           [ 1h] n=1    status=insufficient_n       hit=100% net=+0.00012
· HLP sentiment squeeze (z >= 2.0)           [ 4h] n=1    status=insufficient_n       hit=100% net=-0.00049

## 2026-10-04 18:21 UTC

cycle 33 -- events_fired=0 hyp_generated=0 hyp_promoted=0 new_research_leads=0
👀 CVD / price divergence (BTC, 1h ticks)     [ 4h] n=16   status=insufficient_n_but_promising hit= 62% net=+0.00151
· CVD / price divergence (BTC, 1h ticks)     [ 5m] n=16   status=insufficient_n       hit= 56% net=+0.00091
· CVD / price divergence (BTC, 1h ticks)     [15m] n=16   status=insufficient_n       hit= 56% net=+0.00091
· CVD / price divergence (BTC, 1h ticks)     [ 1h] n=16   status=insufficient_n       hit= 56% net=+0.00091
· Liquidation cascade momentum (5m concentra [ 5m] n=5    status=insufficient_n       hit= 40% net=-0.00047
· Liquidation cascade momentum (5m concentra [15m] n=5    status=insufficient_n       hit= 40% net=-0.00047
· Liquidation cascade momentum (5m concentra [ 1h] n=5    status=insufficient_n       hit= 40% net=-0.00047
· Liquidation cascade momentum (5m concentra [ 4h] n=5    status=insufficient_n       hit= 40% net=-0.00047
· HLP sentiment squeeze (z >= 2.0)           [ 5m] n=1    status=insufficient_n       hit=100% net=+0.00012
· HLP sentiment squeeze (z >= 2.0)           [15m] n=1    status=insufficient_n       hit=100% net=+0.00012
· HLP sentiment squeeze (z >= 2.0)           [ 1h] n=1    status=insufficient_n       hit=100% net=+0.00012
· HLP sentiment squeeze (z >= 2.0)           [ 4h] n=1    status=insufficient_n       hit=100% net=-0.00049

## 2026-10-04 21:44 UTC

cycle 34 -- events_fired=1 hyp_generated=0 hyp_promoted=0 new_research_leads=0
👀 CVD / price divergence (BTC, 1h ticks)     [ 4h] n=16   status=insufficient_n_but_promising hit= 62% net=+0.00151
· CVD / price divergence (BTC, 1h ticks)     [ 5m] n=16   status=insufficient_n       hit= 56% net=+0.00091
· CVD / price divergence (BTC, 1h ticks)     [15m] n=16   status=insufficient_n       hit= 56% net=+0.00091
· CVD / price divergence (BTC, 1h ticks)     [ 1h] n=16   status=insufficient_n       hit= 56% net=+0.00091
· Liquidation cascade momentum (5m concentra [ 5m] n=5    status=insufficient_n       hit= 40% net=-0.00047
· Liquidation cascade momentum (5m concentra [15m] n=5    status=insufficient_n       hit= 40% net=-0.00047
· Liquidation cascade momentum (5m concentra [ 1h] n=5    status=insufficient_n       hit= 40% net=-0.00047
· Liquidation cascade momentum (5m concentra [ 4h] n=5    status=insufficient_n       hit= 40% net=-0.00047
· HLP sentiment squeeze (z >= 2.0)           [ 5m] n=1    status=insufficient_n       hit=100% net=+0.00012
· HLP sentiment squeeze (z >= 2.0)           [15m] n=1    status=insufficient_n       hit=100% net=+0.00012
· HLP sentiment squeeze (z >= 2.0)           [ 1h] n=1    status=insufficient_n       hit=100% net=+0.00012
· HLP sentiment squeeze (z >= 2.0)           [ 4h] n=1    status=insufficient_n       hit=100% net=-0.00049

## 2026-10-05 00:13 UTC

cycle 35 -- events_fired=1 hyp_generated=0 hyp_promoted=0 new_research_leads=0
👀 CVD / price divergence (BTC, 1h ticks)     [ 4h] n=16   status=insufficient_n_but_promising hit= 62% net=+0.00151
· CVD / price divergence (BTC, 1h ticks)     [ 5m] n=17   status=insufficient_n       hit= 53% net=+0.00053
· CVD / price divergence (BTC, 1h ticks)     [15m] n=17   status=insufficient_n       hit= 53% net=+0.00053
· CVD / price divergence (BTC, 1h ticks)     [ 1h] n=17   status=insufficient_n       hit= 53% net=+0.00053
· Liquidation cascade momentum (5m concentra [ 5m] n=5    status=insufficient_n       hit= 40% net=-0.00047
· Liquidation cascade momentum (5m concentra [15m] n=5    status=insufficient_n       hit= 40% net=-0.00047
· Liquidation cascade momentum (5m concentra [ 1h] n=5    status=insufficient_n       hit= 40% net=-0.00047
· Liquidation cascade momentum (5m concentra [ 4h] n=5    status=insufficient_n       hit= 40% net=-0.00047
· HLP sentiment squeeze (z >= 2.0)           [ 5m] n=1    status=insufficient_n       hit=100% net=+0.00012
· HLP sentiment squeeze (z >= 2.0)           [15m] n=1    status=insufficient_n       hit=100% net=+0.00012
· HLP sentiment squeeze (z >= 2.0)           [ 1h] n=1    status=insufficient_n       hit=100% net=+0.00012
· HLP sentiment squeeze (z >= 2.0)           [ 4h] n=1    status=insufficient_n       hit=100% net=-0.00049

## 2026-10-05 05:53 UTC

cycle 36 -- events_fired=1 hyp_generated=0 hyp_promoted=0 new_research_leads=7
why_no_new_hypotheses: OpenRouter call failed: Error code: 401 - {'error': {'message': 'User not found.', 'code': 401}}
👀 CVD / price divergence (BTC, 1h ticks)     [ 4h] n=18   status=insufficient_n_but_promising hit= 67% net=+0.00174
· CVD / price divergence (BTC, 1h ticks)     [ 5m] n=18   status=insufficient_n       hit= 56% net=+0.00081
· CVD / price divergence (BTC, 1h ticks)     [15m] n=18   status=insufficient_n       hit= 56% net=+0.00081
· CVD / price divergence (BTC, 1h ticks)     [ 1h] n=18   status=insufficient_n       hit= 56% net=+0.00081
· Liquidation cascade momentum (5m concentra [ 5m] n=5    status=insufficient_n       hit= 40% net=-0.00047
· Liquidation cascade momentum (5m concentra [15m] n=5    status=insufficient_n       hit= 40% net=-0.00047
· Liquidation cascade momentum (5m concentra [ 1h] n=5    status=insufficient_n       hit= 40% net=-0.00047
· Liquidation cascade momentum (5m concentra [ 4h] n=5    status=insufficient_n       hit= 40% net=-0.00047
· HLP sentiment squeeze (z >= 2.0)           [ 5m] n=1    status=insufficient_n       hit=100% net=+0.00012
· HLP sentiment squeeze (z >= 2.0)           [15m] n=1    status=insufficient_n       hit=100% net=+0.00012
· HLP sentiment squeeze (z >= 2.0)           [ 1h] n=1    status=insufficient_n       hit=100% net=+0.00012
· HLP sentiment squeeze (z >= 2.0)           [ 4h] n=1    status=insufficient_n       hit=100% net=-0.00049

## 2026-10-05 13:54 UTC

cycle 37 -- events_fired=0 hyp_generated=0 hyp_promoted=0 new_research_leads=0
👀 CVD / price divergence (BTC, 1h ticks)     [ 4h] n=19   status=insufficient_n_but_promising hit= 63% net=+0.00121
· CVD / price divergence (BTC, 1h ticks)     [ 5m] n=19   status=insufficient_n       hit= 53% net=+0.00034
· CVD / price divergence (BTC, 1h ticks)     [15m] n=19   status=insufficient_n       hit= 53% net=+0.00034
· CVD / price divergence (BTC, 1h ticks)     [ 1h] n=19   status=insufficient_n       hit= 53% net=+0.00034
· Liquidation cascade momentum (5m concentra [ 5m] n=5    status=insufficient_n       hit= 40% net=-0.00047
· Liquidation cascade momentum (5m concentra [15m] n=5    status=insufficient_n       hit= 40% net=-0.00047
· Liquidation cascade momentum (5m concentra [ 1h] n=5    status=insufficient_n       hit= 40% net=-0.00047
· Liquidation cascade momentum (5m concentra [ 4h] n=5    status=insufficient_n       hit= 40% net=-0.00047
· HLP sentiment squeeze (z >= 2.0)           [ 5m] n=1    status=insufficient_n       hit=100% net=+0.00012
· HLP sentiment squeeze (z >= 2.0)           [15m] n=1    status=insufficient_n       hit=100% net=+0.00012
· HLP sentiment squeeze (z >= 2.0)           [ 1h] n=1    status=insufficient_n       hit=100% net=+0.00012
· HLP sentiment squeeze (z >= 2.0)           [ 4h] n=1    status=insufficient_n       hit=100% net=-0.00049

## 2026-10-05 21:25 UTC

cycle 38 -- events_fired=0 hyp_generated=0 hyp_promoted=0 new_research_leads=0
👀 CVD / price divergence (BTC, 1h ticks)     [ 4h] n=19   status=insufficient_n_but_promising hit= 63% net=+0.00121
· CVD / price divergence (BTC, 1h ticks)     [ 5m] n=19   status=insufficient_n       hit= 53% net=+0.00034
· CVD / price divergence (BTC, 1h ticks)     [15m] n=19   status=insufficient_n       hit= 53% net=+0.00034
· CVD / price divergence (BTC, 1h ticks)     [ 1h] n=19   status=insufficient_n       hit= 53% net=+0.00034
· Liquidation cascade momentum (5m concentra [ 5m] n=5    status=insufficient_n       hit= 40% net=-0.00047
· Liquidation cascade momentum (5m concentra [15m] n=5    status=insufficient_n       hit= 40% net=-0.00047
· Liquidation cascade momentum (5m concentra [ 1h] n=5    status=insufficient_n       hit= 40% net=-0.00047
· Liquidation cascade momentum (5m concentra [ 4h] n=5    status=insufficient_n       hit= 40% net=-0.00047
· HLP sentiment squeeze (z >= 2.0)           [ 5m] n=1    status=insufficient_n       hit=100% net=+0.00012
· HLP sentiment squeeze (z >= 2.0)           [15m] n=1    status=insufficient_n       hit=100% net=+0.00012
· HLP sentiment squeeze (z >= 2.0)           [ 1h] n=1    status=insufficient_n       hit=100% net=+0.00012
· HLP sentiment squeeze (z >= 2.0)           [ 4h] n=1    status=insufficient_n       hit=100% net=-0.00049

## 2026-10-06 01:50 UTC

cycle 39 -- events_fired=1 hyp_generated=0 hyp_promoted=0 new_research_leads=0
👀 CVD / price divergence (BTC, 1h ticks)     [ 4h] n=19   status=insufficient_n_but_promising hit= 63% net=+0.00121
· CVD / price divergence (BTC, 1h ticks)     [ 5m] n=19   status=insufficient_n       hit= 53% net=+0.00034
· CVD / price divergence (BTC, 1h ticks)     [15m] n=19   status=insufficient_n       hit= 53% net=+0.00034
· CVD / price divergence (BTC, 1h ticks)     [ 1h] n=19   status=insufficient_n       hit= 53% net=+0.00034
· Liquidation cascade momentum (5m concentra [ 5m] n=5    status=insufficient_n       hit= 40% net=-0.00047
· Liquidation cascade momentum (5m concentra [15m] n=5    status=insufficient_n       hit= 40% net=-0.00047
· Liquidation cascade momentum (5m concentra [ 1h] n=5    status=insufficient_n       hit= 40% net=-0.00047
· Liquidation cascade momentum (5m concentra [ 4h] n=5    status=insufficient_n       hit= 40% net=-0.00047
· HLP sentiment squeeze (z >= 2.0)           [ 5m] n=1    status=insufficient_n       hit=100% net=+0.00012
· HLP sentiment squeeze (z >= 2.0)           [15m] n=1    status=insufficient_n       hit=100% net=+0.00012
· HLP sentiment squeeze (z >= 2.0)           [ 1h] n=1    status=insufficient_n       hit=100% net=+0.00012
· HLP sentiment squeeze (z >= 2.0)           [ 4h] n=1    status=insufficient_n       hit=100% net=-0.00049

## 2026-10-06 08:28 UTC

cycle 40 -- events_fired=1 hyp_generated=0 hyp_promoted=0 new_research_leads=0
👀 CVD / price divergence (BTC, 1h ticks)     [ 4h] n=20   status=insufficient_n_but_promising hit= 60% net=+0.00096
· CVD / price divergence (BTC, 1h ticks)     [ 5m] n=20   status=insufficient_n       hit= 50% net=+0.00013
· CVD / price divergence (BTC, 1h ticks)     [15m] n=20   status=insufficient_n       hit= 50% net=+0.00013
· CVD / price divergence (BTC, 1h ticks)     [ 1h] n=20   status=insufficient_n       hit= 50% net=+0.00013
· Liquidation cascade momentum (5m concentra [ 5m] n=5    status=insufficient_n       hit= 40% net=-0.00047
· Liquidation cascade momentum (5m concentra [15m] n=5    status=insufficient_n       hit= 40% net=-0.00047
· Liquidation cascade momentum (5m concentra [ 1h] n=5    status=insufficient_n       hit= 40% net=-0.00047
· Liquidation cascade momentum (5m concentra [ 4h] n=5    status=insufficient_n       hit= 40% net=-0.00047
· HLP sentiment squeeze (z >= 2.0)           [ 5m] n=1    status=insufficient_n       hit=100% net=+0.00012
· HLP sentiment squeeze (z >= 2.0)           [15m] n=1    status=insufficient_n       hit=100% net=+0.00012
· HLP sentiment squeeze (z >= 2.0)           [ 1h] n=1    status=insufficient_n       hit=100% net=+0.00012
· HLP sentiment squeeze (z >= 2.0)           [ 4h] n=1    status=insufficient_n       hit=100% net=-0.00049

## 2026-10-06 15:25 UTC

cycle 41 -- events_fired=1 hyp_generated=0 hyp_promoted=0 new_research_leads=0
· CVD / price divergence (BTC, 1h ticks)     [ 5m] n=21   status=insufficient_n       hit= 48% net=-0.00018
· CVD / price divergence (BTC, 1h ticks)     [15m] n=21   status=insufficient_n       hit= 48% net=-0.00018
· CVD / price divergence (BTC, 1h ticks)     [ 1h] n=21   status=insufficient_n       hit= 48% net=-0.00018
· CVD / price divergence (BTC, 1h ticks)     [ 4h] n=21   status=insufficient_n       hit= 57% net=+0.00061
· Liquidation cascade momentum (5m concentra [ 5m] n=5    status=insufficient_n       hit= 40% net=-0.00047
· Liquidation cascade momentum (5m concentra [15m] n=5    status=insufficient_n       hit= 40% net=-0.00047
· Liquidation cascade momentum (5m concentra [ 1h] n=5    status=insufficient_n       hit= 40% net=-0.00047
· Liquidation cascade momentum (5m concentra [ 4h] n=5    status=insufficient_n       hit= 40% net=-0.00047
· HLP sentiment squeeze (z >= 2.0)           [ 5m] n=1    status=insufficient_n       hit=100% net=+0.00012
· HLP sentiment squeeze (z >= 2.0)           [15m] n=1    status=insufficient_n       hit=100% net=+0.00012
· HLP sentiment squeeze (z >= 2.0)           [ 1h] n=1    status=insufficient_n       hit=100% net=+0.00012
· HLP sentiment squeeze (z >= 2.0)           [ 4h] n=1    status=insufficient_n       hit=100% net=-0.00049

## 2026-10-06 20:30 UTC

cycle 42 -- events_fired=0 hyp_generated=0 hyp_promoted=0 new_research_leads=0
👀 CVD / price divergence (BTC, 1h ticks)     [ 4h] n=22   status=insufficient_n_but_promising hit= 59% net=+0.00090
· CVD / price divergence (BTC, 1h ticks)     [ 5m] n=22   status=insufficient_n       hit= 50% net=+0.00014
· CVD / price divergence (BTC, 1h ticks)     [15m] n=22   status=insufficient_n       hit= 50% net=+0.00014
· CVD / price divergence (BTC, 1h ticks)     [ 1h] n=22   status=insufficient_n       hit= 50% net=+0.00014
· Liquidation cascade momentum (5m concentra [ 5m] n=5    status=insufficient_n       hit= 40% net=-0.00047
· Liquidation cascade momentum (5m concentra [15m] n=5    status=insufficient_n       hit= 40% net=-0.00047
· Liquidation cascade momentum (5m concentra [ 1h] n=5    status=insufficient_n       hit= 40% net=-0.00047
· Liquidation cascade momentum (5m concentra [ 4h] n=5    status=insufficient_n       hit= 40% net=-0.00047
· HLP sentiment squeeze (z >= 2.0)           [ 5m] n=1    status=insufficient_n       hit=100% net=+0.00012
· HLP sentiment squeeze (z >= 2.0)           [15m] n=1    status=insufficient_n       hit=100% net=+0.00012
· HLP sentiment squeeze (z >= 2.0)           [ 1h] n=1    status=insufficient_n       hit=100% net=+0.00012
· HLP sentiment squeeze (z >= 2.0)           [ 4h] n=1    status=insufficient_n       hit=100% net=-0.00049

