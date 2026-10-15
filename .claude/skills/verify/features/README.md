# SportsJobs scraper verification map

This directory is the maintained source for verifying what the scrapers produce: the rows they would insert into the production `jobs` table. Read this index first, then use the matching feature file.

## Baseline preconditions

- Work from the repo root, with `.env` present.
- `PYTHONIOENCODING=utf-8 poetry run python .claude/skills/verify/scripts/dry_run.py --doctor` prints `READY`.
- Selenium runners need local Chrome.

## Driving conventions

- Drive the script that `run_scripts.sh` calls, through `dry_run.py`. Never run it with plain `python`.
- Narrow a run by temporarily commenting out other entries in `companies` / `teams`, then restore them.
- Only scraper scripts (everything before `indexing_sportsjobs.py` in `run_scripts.sh`) are in scope.

## Proof and skip reporting

- Proof is the captured insert in `.verify-evidence/<ts>-<script>.json` for the target company or class, with its key fields quoted.
- A target with no captured insert needs the log line explaining why, from the matching `.log`.
- Report a runner you could not drive (for example, no Chrome) as unverified. Do not count it as verified through a different runner.

## Features

- [Modern ATS scrapers](./ats-companyscraper.md): Workable and Workday, built on `CompanyScraper` and JSON APIs.
- [Legacy ATS scripts](./ats-legacy-scripts.md): Lever, Greenhouse, Ashby, Rippling and Personio, top-level scripts with a `companies` dict.
- [Sport and source page runners](./page-runners.md): `scrape_<sport>/*_scrapers.py` Selenium/HTTP `CompanyScraper` classes, including TeamWork Online.
