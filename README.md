# DRF Race of the Day Tracker

A daily agent handicaps DRF's free Race of the Day with the handicap-race method and records a top pick and a second choice. It grades the previous day's result and tracks two paper strategies:

- **Top Pick:** $2 Win + $2 Place + $2 Show ($6) on the top pick
- **Top 2 Picks:** the same $6 on the top pick and on the second choice ($12 per race)

No real bets are placed.

**Results page:** `docs/index.html`, published with GitHub Pages.

| File | What it is |
|---|---|
| `ledger.csv` | One row per race: both picks, results and payouts (the source of truth) |
| `handicaps/` | The full write-up for each race |
| `build_site.py` | Builds the mobile results page (`docs/index.html`) from the ledger |
| `build_workbook.py`, `refresh_excel.ps1` | Build the local Excel dashboard (not committed) |
| `AGENT_INSTRUCTIONS.md` | What the daily agent does |
| `run-log.md` | One line per daily run |
