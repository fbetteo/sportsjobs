# SportsJobs scraper: guide for coding agents

This repository collects sports analytics, data, and software jobs for SportsJobs.online. Keep changes focused and explicit. Read the relevant existing scraper before adding a new one; prefer a small addition to an established pattern over a new framework or service.

## Related repositories

The SportsJobs application also has two sibling repositories under `C:\Users\franb\projects\sportsjobs\`:

- Frontend: `C:\Users\franb\projects\sportsjobs\sportsjobs-frontend` (Next.js app). Start with its `AGENTS.md`, then the relevant topic document in `docs/` and current code.
- Backend and database setup: `C:\Users\franb\projects\sportsjobs\sportsjobs_postgres` (FastAPI, PostgreSQL, API endpoints, and database scripts). Start with its `AGENTS.md`, then the relevant topic document in `docs/` and current code.

For a feature spanning repositories, first identify which repo owns each part: user interface and browser interactions in the frontend; API, persistence, and database changes in `sportsjobs_postgres`; job collection and enrichment in this scraper. Check the existing API and database fields before changing a producer or consumer, and keep field names and behavior coordinated across the affected repos. Follow each repo's own instructions and test the changed boundary with a small focused example. A CV collection feature, for example, may only need frontend and backend work unless the scraper has an actual role in processing those CVs. Do not add scraper code just because a feature belongs to SportsJobs.

## Start here

- `run_scripts.sh` is the main production entry point and the source of truth for **which scripts run** and their order. It runs ATS scrapers first, then sport/source scrapers, followed by indexing, scheduled social posts, newsletter processing, expiration handling, and scheduled Airtable work. A file that is not called from this script (or from a called script) is not part of this pipeline.
- `lever_scrapper.py`, `greenhouse_scrapper.py`, `ashbyhq.py`, `rippling_scraper.py`, and `personio_scraper.py` scrape companies using their respective ATS APIs/feeds. Their `companies` dictionaries are the first place to look when adding a company on an already supported ATS.
- `scrape_<sport>/` and source folders such as `scrape_others/` contain page-specific Selenium scrapers. Look at the entry point actually called by `run_scripts.sh`, for example `scrape_nba/nba_scrapers.py` or `scrape_soccer/clubs_scrapers.py`. Some folders also contain older individual files that the runner does not call.
- `base_scraper/companyscraper.py` defines `CompanyScraper`, the shared flow for browser-based pages: find listings, scrape each job, enrich/filter it, and insert it. `utils.py` contains job classification and enrichment helpers. `hetzner_utils.py` contains PostgreSQL connection, lookup, and insert helpers. Inspect these before duplicating shared behavior.
- `indexing_sportsjobs.py`, `deindex_expired_jobs.py`, `post_to_linkedin.py`, `twitter_bot.py`, `newsletter_email_sequence.py`, and `airtable_api.py` are downstream jobs. Changes to these can have external effects beyond scraping.

## Adding coverage

1. Identify the site's ATS or feed before writing browser automation. If it uses an ATS already covered here, add its company settings to that script's `companies` dictionary and follow that script's existing API, filtering, logo, and record conventions.
2. For a custom page, add a `CompanyScraper` subclass to the appropriate sport/source runner. Follow a nearby working class: set `company`, `logo`, and `base_url`; implement `open_site()`, `get_jobs_available()` (return `{"title": ..., "url": ...}` items), and `_scrape_job()` (return `job`, `location_value`, `hours`, and `full_description`, with optional `other_data`). Use explicit waits for dynamic pages and release the shared Selenium driver when the runner finishes.
3. Register a new class in that runner's active `teams` list. For a new sport or source runner, add its Python invocation to `run_scripts.sh` in the scraper section, before indexing, and handle a nonzero exit as the neighboring calls do. Merely defining a class or file does not make it run.
4. Keep the current job selection rules in mind: recent URLs are used to avoid duplicates, and descriptions/skills determine whether a job qualifies. Check the output against the existing `jobs` record fields before inserting; use the established enrichment and PostgreSQL helpers where they fit.
5. For new features outside scraping, locate the closest existing script and its position in `run_scripts.sh`. Add shared code to `utils.py` or `hetzner_utils.py` only when multiple callers actually need it. Do not create a generic scraper engine, registry, queue, or extra service for a single new page.

## Style and environment

- Follow the style of the relevant working script, but make new code small, readable, and explicit. Prefer named helpers, straightforward loops, and narrow exception handling. Avoid copying large commented-out sections from older scrapers.
- This is a Poetry project (`pyproject.toml`, `poetry.lock`); keep Poetry as the dependency manager. The `requirements.txt` and Dockerfile reflect an older deployment setup. Do not silently migrate package management or delete those files. The declared Poetry Python requirement is `^3.12`, while the Dockerfile currently starts from Python 3.11; treat deployment changes as a separate, reviewable task.
- Configuration comes from environment variables and `.env`. Never put credentials, tokens, or service-account JSON contents in code, tests, logs, or documentation. PostgreSQL writes, Airtable calls, indexing, email, and social posting may affect live systems.
- Do not run `run_scripts.sh` as a routine test: it performs real inserts and external actions. Validate a new parser or scraper with a small local fixture/mocked response and a focused test where behavior is nontrivial. For a documentation-only change, check paths and script names against the current files. Run the full pipeline only when the task explicitly calls for an integration run in an appropriate environment.
- Existing tests use `unittest` (`test_alert_matching.py`, `test_deindex_expired_jobs.py`). Keep tests focused on decisions and transformations, rather than repeating implementation details.

## When editing the pipeline

Read the complete `run_scripts.sh` block you change, including its failure behavior and day-of-week condition. Keep scraping before indexing and downstream jobs. The shell script currently mixes `python3` and `python`, and some schedule comments/messages disagree with the actual Monday-through-Thursday condition; rely on executable conditions when reasoning about behavior. Avoid unrelated cleanup in a feature change, but mention operational inconsistencies that affect the task.
