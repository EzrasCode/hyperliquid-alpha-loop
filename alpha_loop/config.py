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

# How often the loop pulls fresh data and evaluates hypotheses. 5 minutes
# matches the shortest forward-return horizon (HORIZONS_MINUTES in
# hypothesis_bank.py) and the API's own ~20s-5min data update cadence. This
# is also the GitHub Actions schedule interval -- see the workflow file.
CYCLE_INTERVAL_SECONDS = 300

# Ask the LLM for new hypothesis parameterizations every N cycles (12 cycles
# * 5 min = hourly) -- keeps OpenRouter cost bounded on a 24/7 process.
IDEA_GEN_EVERY_N_CYCLES = 12
IDEA_GEN_MAX_NEW_PER_CALL = 3

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
