"""
Fixed parameters for the autonomous alpha-mining loop.
Decided in docs/research/alpha_loop/alpha_loop_overview_20260927.md -- don't
change these without re-reading that doc and, for anything that changes what
counts as a "hit," logging why in docs/research/alpha_loop/decision_log.md.

This loop is READ-ONLY RESEARCH. It never places an order and never reads a
private key. It pulls Hyperliquid data, records candidate signals, and scores
them for statistical significance so a human can decide whether any of them
are worth building into an actual strategy. See the overview doc for why.

Deployed via GitHub Actions (see .github/workflows/alpha_loop.yml): each
scheduled run does ONE cycle (`python -m alpha_loop.loop --once`) against a
fresh checkout, then commits alpha_loop.db and the decision log back to the
repo so state survives between runs -- there is no long-lived process.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

DB_PATH = Path(__file__).resolve().parent / "alpha_loop.db"
DECISION_LOG_PATH = REPO_ROOT / "docs" / "research" / "alpha_loop" / "decision_log.md"
RESEARCH_LEADS_DOC_PATH = REPO_ROOT / "docs" / "research" / "alpha_loop" / "research_leads.md"

# How often the loop pulls fresh data and evaluates hypotheses. 5 minutes
# matches the shortest forward-return horizon (HORIZONS_MINUTES in
# hypothesis_bank.py) and the API's own ~20s-5min data update cadence. This
# is also the GitHub Actions schedule interval -- see the workflow file.
CYCLE_INTERVAL_SECONDS = 300

# Ask the LLM for new hypothesis parameterizations every N cycles (12 cycles
# * 5 min = hourly) -- keeps OpenRouter cost bounded on a 24/7 process.
IDEA_GEN_EVERY_N_CYCLES = 12
IDEA_GEN_MAX_NEW_PER_CALL = 3

# How often to check arXiv for new relevant papers (12 cycles * 5 min =
# hourly, same cadence as idea generation -- see research_scout.py).
RESEARCH_SCOUT_EVERY_N_CYCLES = 12

# Universe this loop watches. Matches Ideas.md's own BTC-centric live setup
# plus the handful of coins the order-flow/tick endpoints actually cover.
UNIVERSE = ["BTC", "ETH", "SOL", "XRP", "HYPE"]

# Explicit fee assumption for fee-adjusted mean return, same convention as
# the aitrading project's funding-carry analysis: taker fee both sides plus
# slippage, stated up front rather than ignored.
ROUND_TRIP_FEE_FRACTION = 0.0010  # 0.10%

# Model used for idea generation via OpenRouter (needs OPENROUTER_API_KEY as
# a GitHub Actions secret). Kept to a single, cheap-ish model rather than a
# multi-model fan-out to control cost on a process that runs every hour,
# forever.
IDEA_GEN_MODEL = "anthropic/claude-sonnet-4"

# Rate-limit budget: stay well under the documented 3,600 req/min.
MAX_REQUESTS_PER_MINUTE = 120
RETRY_MAX_ATTEMPTS = 4
RETRY_BASE_BACKOFF_SECONDS = 2.0

# --- Statistical validity gates (see docs/research/alpha_loop/evidence_schema.md) ---
# Below MIN_N, a hit rate or mean return is noise, not a finding -- the report
# and Discord output mark these "insufficient_n" instead of printing a number
# that looks meaningful. 30 is the conventional rule-of-thumb minimum sample
# size for the normal approximation to the t-distribution to be reasonable.
MIN_N_FOR_SIGNIFICANCE = 30
MIN_ABS_T_STAT = 2.0
MIN_MFE_MAE_RATIO = 1.5
MAX_BOOTSTRAP_P = 0.05
BOOTSTRAP_ITERATIONS = 2000
BOOTSTRAP_BLOCK_SIZE = 5  # contiguous-block resampling to respect autocorrelation

# Explicit execution-cost assumptions, separate from each other so gross vs.
# net is never ambiguous in the output (same "state your fee assumption"
# convention as the funding-carry analysis this project is built alongside).
TAKER_FEE_BPS = 4.5     # Hyperliquid taker fee, one side
SLIPPAGE_BPS = 2.0       # modeled, not measured -- no live fills exist yet
ROUND_TRIP_COST_FRACTION = 2 * (TAKER_FEE_BPS + SLIPPAGE_BPS) / 10_000

# Kept for backward compatibility with earlier runs' stored assumption.
ROUND_TRIP_FEE_FRACTION = ROUND_TRIP_COST_FRACTION

# Simplified trading-session buckets (UTC hour ranges) for conditioning
# hypothesis stats by session -- see market_context.py.
SESSION_WINDOWS_UTC = [
    ("Asia", 0, 8),
    ("London", 8, 13),
    ("NY", 13, 21),
    ("Late", 21, 24),
]

# How many hours of this loop's own accumulated price panel to use for the
# realized-vol/regime heuristic, and how many historical comparison windows
# are required before a percentile/regime label is trusted rather than
# reported as "insufficient_history". The loop has no deep historical data
# (see backtest_engine.py's docstring) so both numbers start small and this
# context enrichment genuinely only becomes meaningful after days of running.
VOL_LOOKBACK_HOURS = 1
MIN_HISTORY_WINDOWS_FOR_PERCENTILE = 10
