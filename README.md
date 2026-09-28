# Hyperliquid Alpha Loop

A read-only research bot that mines Moon Dev's Hyperliquid Data Layer API for
candidate trading signals, scores them for statistical significance over
time, and posts every cycle's results to Discord. Runs on a GitHub Actions
schedule -- no server to maintain, no long-lived process.

**This never places an order and never touches a private key.** It only
reads public/API data and writes research results (a SQLite database and a
markdown decision log) back to this repo. See
`docs/research/alpha_loop/alpha_loop_overview_20260927.md` for the full
methodology and the five seed hypotheses.

## Setup

1. **Get a Moon Dev API key**: https://moondev.com (free tier is enough to
   start).
2. **(Optional) Get an OpenRouter key**: https://openrouter.ai -- powers the
   hourly "propose new hypothesis parameterizations" step. Without it the
   loop still runs every cycle, it just never generates new ideas.
3. **(Optional) Create a Discord webhook**: in your server, Server Settings
   -> Integrations -> Webhooks -> New Webhook -> pick a channel -> Copy
   Webhook URL. Use a dedicated channel/webhook for this bot rather than
   sharing one with other bots -- Discord rate-limits per webhook.
4. **Add repo secrets**: on GitHub, go to this repo's Settings -> Secrets and
   variables -> Actions -> New repository secret, and add:
   - `MOONDEV_API_KEY` (required)
   - `OPENROUTER_API_KEY` (optional)
   - `DISCORD_WEBHOOK_URL` (optional)
5. **Enable Actions**: go to the Actions tab and enable workflows if prompted
   (first-time enable is required on a fresh repo). The workflow
   (`.github/workflows/alpha_loop.yml`) is scheduled every 5 minutes and can
   also be triggered manually via "Run workflow" to test it immediately.

That's it -- once secrets are set and Actions is enabled, it runs itself.
Each run commits its results (`alpha_loop/alpha_loop.db`,
`docs/research/alpha_loop/decision_log.md`) back to `main`.

## Local development

```
pip install -r requirements.txt
cp .env.example .env   # fill in MOONDEV_API_KEY at minimum
python -m alpha_loop.loop --once      # one cycle
python -m alpha_loop.report_top_ideas  # ranked leaderboard
```

## Repo layout

- `alpha_loop/` -- the loop itself (config, data fetching, hypothesis bank,
  event-study backtest engine, SQLite store, idea generator, Discord notify)
- `vendor/moondev_api.py` -- unmodified copy of Moon Dev's API client
- `docs/research/alpha_loop/` -- methodology doc + append-only decision log
- `.github/workflows/alpha_loop.yml` -- the scheduled deployment
