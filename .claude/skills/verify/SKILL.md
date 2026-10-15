---
name: verify
description: Prove a SportsJobs scraper change works by running the real scraper script against the live job sites with PostgreSQL stubbed out, capturing the exact `jobs` rows it would insert. Use after adding a company to an ATS `companies` dict, adding or editing a CompanyScraper class, or changing enrichment in utils.py / base_scraper, before claiming the change works.
---

# Verify SportsJobs scrapers

The product surface of this repo is the rows that scrapers insert into the production `jobs` table. Nothing local can be inserted safely: `hetzner_utils.insert_records` writes to live PostgreSQL. So verification runs the real, unmodified pipeline script, but through `scripts/dry_run.py`, which replaces the database layer before the script loads:

- `insert_records` → captured into a JSON evidence file, never written.
- `get_recent_urls`, `get_urls_by_domain`, `get_skills` → return `[]` (no duplicate filtering, see Gotchas).
- `start_postgres_connection` → in-memory fake; `psycopg2.connect` raises if anything tries a real connection.

Everything else is real: the job sites/ATS APIs, Selenium, the Airtable schema read used by `utils.get_skills_required`, and Nominatim geocoding.

Never run `run_scripts.sh`, and never run a scraper with plain `python <script>`: both insert into production. Do not dry-run anything after the scraper section of `run_scripts.sh` (indexing, social posts, alerts, newsletters, deindexing, Airtable): those send email, posts and index requests that this harness does not intercept.

## Launch

There is no server. Each verification is one process. Run from the repo root (`C:\Users\franb\projects\sportsjobs\sportsjobs`):

```bash
PYTHONIOENCODING=utf-8 poetry run python .claude/skills/verify/scripts/dry_run.py <repo-relative script>
# e.g.
PYTHONIOENCODING=utf-8 poetry run python .claude/skills/verify/scripts/dry_run.py workable_scraper.py
```

It loads `.env` itself. Poetry resolves to the conda env `sportsjobs` (Python 3.12). Done means the process prints `[dry run] exit code N, K captured inserts` followed by the evidence paths. A small ATS script takes about 10 seconds; Lever/Greenhouse/Ashby loop over many companies and take minutes; Selenium runners take longer.

## Doctor

Run first, and again whenever anything looks off:

```bash
PYTHONIOENCODING=utf-8 poetry run python .claude/skills/verify/scripts/dry_run.py --doctor
```

It prints `READY` (exit 0) when `.env` exists, the Airtable env vars are set, the scraper dependencies import, and the Airtable jobs schema with its `skills` field can be read. Anything else prints `NOT READY` and the failing line. Selenium runners also need local Chrome. The doctor does not check that.

## Drive

Pick the script that `run_scripts.sh` actually calls for the code you changed (see `features/README.md`), and dry-run that script. To target one new company or class, comment out the others locally in the script's `companies` dict or `teams` list for the run, then restore it with `git diff` checked clean. Do not commit that edit.

## Evidence

Each run writes two files to `.verify-evidence/` at the repo root (gitignored):

- `<timestamp>-<script>.json` contains `{script, exit_code, inserts: [{table, data}]}`, where `data` is the exact column dict that would have been inserted into `jobs`.
- `<timestamp>-<script>.log` holds the full console output of the run.

Proof standard:

- Show that the changed company or class produced a captured insert, by quoting its `name`, `url`, `company`, `country`/`country_code`, `skills`, `location` and `logo_permanent_url` from the JSON.
- Or show the log line that explains why it was filtered, such as `has no skills required, skipping...`.
- A run that exits 0 with zero inserts for the target is not proof that it works. Find the reason in the log.

Read the JSON with UTF-8 output, because job text has non-ASCII characters and the Windows console is cp1252:

```bash
PYTHONIOENCODING=utf-8 poetry run python -c "import json,sys; d=json.load(open(sys.argv[1],encoding='utf-8')); print(d['exit_code'], len(d['inserts'])); [print(i['data']['company'], '|', i['data']['name'], '|', i['data']['url']) for i in d['inserts']]" .verify-evidence/<file>.json
```

## Cleanup

The harness starts no background processes. Selenium runners quit their own driver at the end of the script. If a run is interrupted, close only the Chrome/chromedriver processes that run started, never all of them by name. Restore any local `companies`/`teams` edits (`git diff` must be clean apart from your real change). Leave `.verify-evidence/` in place, because it holds the proof. Delete old files there only when the user asks.

## Helpers

- `scripts/dry_run.py <script>` dry-runs one pipeline script and writes the evidence.
- `scripts/dry_run.py --doctor` checks the environment is ready.
- For pure parsing logic, the repo also has `unittest` suites: `poetry run python -m unittest test_workable_scraper test_workday_scraper test_alert_matching`.

## Gotchas

- Duplicate filtering is off, because the recent-URL reads return `[]`. A dry run therefore reports every matching job, including ones already in production. That is expected, and is not a dedupe bug.
- The DB `skills` list is empty in a dry run. The legacy ATS scripts fall back to their hardcoded `skills_to_search`, so skill matching can differ slightly from production.
- Any scraper that uses `base_scraper/teamworkonline.py` sends requests through the paid proxy (`TEAMWORK_PROXY_URL`). It also updates the local `teamwork_rejected_urls.json` cache for real. Dry-run those runners only when the change needs it.
- `scrape_scottspower/scottspower_scrapers.py` sends a `requests.post` to an external trigger API. Read it before dry-running.
- If a run fails with `dry run: raw SQL is not stubbed` or `real PostgreSQL connection attempted`, the script reached the DB another way. Extend `stub_database` in `dry_run.py` rather than bypassing the harness.
