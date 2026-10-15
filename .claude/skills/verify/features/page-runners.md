# Sport and source page runners

Each `scrape_<sport>/` runner defines `CompanyScraper` subclasses for team or league career pages and runs every class in its `teams` list with one shared headless Chrome driver. Some classes fetch TeamWork Online over plain HTTP through a proxy.

## Sub-features

- `selenium-page` covers a class that opens a careers page in Chrome, lists jobs and scrapes each one.
- `teamworkonline` covers classes built on `base_scraper/teamworkonline.py`, which use HTTP through `TEAMWORK_PROXY_URL` and a rejected-URL cache.
- `runner` covers the `scrape_<sport>/<sport>_scrapers.py` entry point called from `run_scripts.sh`.

## How to get to it (user POV)

- Add a class to a runner and register it in that runner's `teams` list.
- The pipeline runs, for example, `python scrape_nba/nba_scrapers.py`. The full list is in `run_scripts.sh`.

## Driving it with dry_run.py

Preconditions:

- Doctor prints `READY`, and Chrome is installed.
- Temporarily reduce `teams` to the class under test, then restore it.

- **Run.** `PYTHONIOENCODING=utf-8 poetry run python .claude/skills/verify/scripts/dry_run.py scrape_nba/nba_scrapers.py`. The log shows `Running <Class> main()` and then one captured insert per qualifying job.
- **Inspect.** The captured rows have `company` and `logo_permanent_url` from the class attributes, and URLs under the class's `base_url`.

## Gotchas

- Not yet proven with the harness. The first run here should record its result in this file.
- TeamWork Online classes spend paid proxy requests and write `teamwork_rejected_urls.json` for real.
- `main()` retries 3 times and then gives up quietly, with `Max retries reached. Exiting this <company>...`. Exit code 0 does not mean the class worked.
- An interrupted run can leave a headless Chrome running. Close only the processes that run started.
