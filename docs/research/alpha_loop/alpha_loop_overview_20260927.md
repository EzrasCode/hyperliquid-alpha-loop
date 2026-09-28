# Autonomous Hyperliquid Alpha-Mining Loop

Date: 2026-09-27 (moved to its own public repo 2026-09-28 for GitHub Actions
deployment; original design lives in the private `aitrading` repo's history)

## What this is

A process (`alpha_loop/`) that pulls Hyperliquid Data Layer API data on a
5-minute cycle, evaluates a bank of candidate trading signals against it,
records which ones fire, and scores their forward returns for statistical
significance once enough wall-clock time has passed. It is **read-only
research** -- no order placement, no private key, no live capital anywhere
in this repo. Output is a ranked leaderboard (`report_top_ideas.py`) plus a
Discord post every cycle, for a human to review before deciding whether any
hypothesis is worth building into an actual strategy.

## Why this repo is separate and public

This started as a module inside a private trading-research repo. It was
split out here so it can run unattended on GitHub Actions: Actions minutes
are free/unlimited on public repos (capped on private ones), and this repo
never contains account size, leverage, or strategy decisions -- only the
generic, read-only signal-mining research and its own decision log.

## Why the data layer's own history isn't enough

Moon Dev's API keeps only a shallow window of historical candles/ticks/
liquidation events -- not enough to backtest most of these ideas against
deep history. Rather than pretend otherwise, this loop builds its **own**
live panel over time: every cycle it snapshots current prices and any fired
signals into `alpha_loop/alpha_loop.db` (committed back to the repo after
every run so state survives GitHub Actions' disposable runners), then
resolves each signal's forward return only once that much real time has
actually elapsed (5m/15m/1h/4h horizons). Statistical power accumulates the
longer this keeps running.

## The five seed hypotheses

1. **HLP sentiment squeeze** (`/api/hlp/sentiment`) -- HLP positioning is
   the inverse of retail positioning; an extreme z-score predicts a
   short-horizon squeeze. Two parameterizations seeded (z>=2.0, z>=2.5).
2. **Liquidation cascade momentum** (`/api/all_liquidations/totals.json`) --
   liquidation volume concentrated in the most recent 5-minute window (vs.
   the trailing 15m) signals an in-progress cascade likely to continue.
3. **Smart-money top signal** (`/api/smart_money/signals_{tf}.json`) --
   following the highest-confidence signal from the Top-100-by-PnL cohort.
4. **CVD / price divergence** (tick-rule cumulative volume delta vs. price)
   -- textbook order-flow divergence, tested for whether it actually holds
   on this venue.
5. **Cross-exchange liquidation lead-lag** -- a large Binance liquidation
   spike with little corresponding Hyperliquid liquidation yet, predicting
   HL liquidations are still coming.

## How new ideas get generated

Every hour, the loop sends OpenRouter a summary of current hypothesis stats
and asks for new *parameterizations* of the same five evaluator kinds -- new
thresholds, coins, or timeframes. It cannot write new signal logic: its JSON
output is validated against a fixed param schema and only ever changes
numbers/coins, never code. The loop never `eval()`s or `exec()`s anything an
LLM produces. Adding a genuinely new signal kind requires a human to write a
new evaluator function in `alpha_loop/backtest_engine.py`.

## Research scouting (arXiv, Semantic Scholar, Quantocracy, Reddit, GitHub)

Every hour, alongside idea generation, `research_scout.py` checks five free,
ToS-compliant sources for candidate leads matching keywords relevant to this
loop's signals (liquidation, order flow, market microstructure,
momentum/mean-reversion, cointegration):

- **arXiv** -- recent papers in quant-finance categories (q-fin.TR/ST/CP).
- **Semantic Scholar** -- broader academic coverage (journals, SSRN-indexed
  working papers), also free, no key needed.
- **Quantocracy** -- a curated daily aggregator of quant-trading blog posts.
- **Reddit** (r/algotrading, r/quant) -- forum discussion, noisier signal
  than the above but zero cost.
- **GitHub** -- newly-updated open-source repos matching trading-strategy
  keywords, a proxy for what practitioners are actually building.

Google Scholar and X/Twitter search were both considered and excluded:
Scholar has no API and blocks scraping; X's search API now requires a paid
tier (~$200/mo). Books, podcasts, and videos were also considered -- there's
no free/legal way to extract their actual content for an unattended bot
(YouTube's API only searches titles/descriptions, not what's said in a
video), so those require a human to read/watch and manually propose the
resulting idea.

New leads (deduped by `(source, external_id)`) are posted to Discord and
appended to `docs/research/alpha_loop/research_leads.md`. Same safety
boundary as idea generation: a lead is a human-readable pointer, never
auto-converted into a running signal.

## Deployment

`.github/workflows/alpha_loop.yml` runs every 5 minutes: checks out the
repo, runs one cycle (`python -m alpha_loop.loop --once`), posts the summary
to Discord, then commits the updated `alpha_loop.db` and decision log back
to the repo. Required GitHub repo secrets: `MOONDEV_API_KEY` (required),
`OPENROUTER_API_KEY` and `DISCORD_WEBHOOK_URL` (both optional -- the loop
degrades gracefully without them). See the repo README for setup steps.

## Reading the output

`python -m alpha_loop.report_top_ideas` prints every hypothesis/horizon with
n, hit rate, mean return, and both a raw and fee-adjusted (0.10% round-trip)
t-stat. Treat anything under ~20 samples as noise; a real signal should hold
up as n grows over weeks of continuous running, not just look good on day
one.

## Ideas tested and rejected

(none yet -- to be filled in as the loop accumulates enough samples per
hypothesis to say something statistically meaningful)
