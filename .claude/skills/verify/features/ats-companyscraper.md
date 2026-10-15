# Modern ATS scrapers

Workable and Workday companies are listed in a `COMPANIES` dict and scraped through public JSON endpoints by `CompanyScraper` subclasses. Matching jobs are enriched and inserted as `jobs` rows.

## Sub-features

- `workable` covers `workable_scraper.py`, one entry per Workable account.
- `workday` covers `workday_scraper.py`, one entry per Workday tenant.
- `enrich` covers the shared enrichment (skills, country, remote, seniority, sport, industry) in `CompanyScraper._enrich_and_format_job`.

## How to get to it (user POV)

- Add a company to `COMPANIES` in `workable_scraper.py` or `workday_scraper.py`.
- The pipeline runs `python workable_scraper.py` / `python workday_scraper.py` from `run_scripts.sh`.

## Driving it with dry_run.py

Preconditions:

- Doctor prints `READY`.

- **Run.** `PYTHONIOENCODING=utf-8 poetry run python .claude/skills/verify/scripts/dry_run.py workable_scraper.py`. The output ends with `exit code 0, N captured inserts`. The log shows `Found N new matching Workable jobs for <Company>`.
- **Inspect.** Print the inserts from the JSON (command in SKILL.md). Each row has `company` set to the dict key, a canonical `https://apply.workable.com/<account>/j/<code>` URL, `country`/`country_code`, `logo_permanent_url`, and a non-empty `skills` list.
- **Filtered jobs.** Jobs without at least two required skills log `Job <title> has no skills required, skipping...` and have no insert.
- **Proven 2026-10-15.** Rapsodo (Workable) gave exit 0 with 15 captured inserts in about 9 s.

## Gotchas

- `skills` in captured rows can contain duplicates, such as `'AI', 'AI'`. That comes from `utils.get_skills_required`, not from the harness.
- Duplicate filtering is off in a dry run, so already-published jobs reappear.
