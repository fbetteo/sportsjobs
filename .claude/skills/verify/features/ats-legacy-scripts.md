# Legacy ATS scripts

Lever, Greenhouse, Ashby, Rippling and Personio are top-level scripts. Each opens a DB connection at import, loops over a `companies` dict inside its run block, filters by keywords and skills, and calls `insert_records` directly.

## Sub-features

- `lever` covers `lever_scrapper.py`.
- `greenhouse` covers `greenhouse_scrapper.py`.
- `ashby` covers `ashbyhq.py`.
- `rippling` covers `rippling_scraper.py`.
- `personio` covers `personio_scraper.py`.

## How to get to it (user POV)

- Add a company to the `companies` dict in the matching script.
- The pipeline runs each script in this order at the top of `run_scripts.sh`.

## Driving it with dry_run.py

Preconditions:

- Doctor prints `READY`.
- For a single new company in Lever, Greenhouse or Ashby, temporarily comment out the other `companies` entries, because the full dict takes minutes.

- **Run.** `PYTHONIOENCODING=utf-8 poetry run python .claude/skills/verify/scripts/dry_run.py personio_scraper.py`. The log shows `[dry run] captured insert into jobs: <title> <url>` and the script's own `Inserted job: <title> at <company>`.
- **Inspect.** Print the inserts from the JSON. The target company appears in `company`, with its URL on that ATS's domain.
- **Proven 2026-10-15.** Personio gave exit 0 with 1 captured insert (PACETEQ) in about 7 s. This exercises the module-level fake connection path.

## Gotchas

- These scripts catch their own errors and still exit 0. Read the log for `Error occurred:` lines.
- Personio currently logs `Error occurred: 'NoneType' object has no attribute 'text'` after the first PACETEQ posting. This is a real pre-existing parsing failure in `personio_scraper.py`, where a `position.find(...)` returns `None`, and it is not caused by the harness. Any postings after the failure point are skipped.
- `get_skills` returns `[]` here, so skill matching uses only each script's hardcoded `skills_to_search`.
