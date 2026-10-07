"""One-off backfill for job countries written by the old location parser.

The old clean_location split on bare substrings ("Baltimore" -> "baltim" -> Egypt), find_country
silently defaulted to the US on geocoder timeouts, and Lever stored unmapped ISO codes ("hr").
This recomputes only rows that bug could have affected, so a geocoder answer never overwrites a
country the old code got from the same input.

Usage (on the server, where the scraper's PostgreSQL connection works):
    python backfill_job_countries.py            # dry run: prints proposed changes
    python backfill_job_countries.py --apply    # writes them in one transaction
"""

import argparse
import re

import utils


def legacy_clean_location(location):
    """The pre-fix parser, kept only to detect rows it mangled."""
    location = location.lower()
    location = location.split("/")[0]
    location = location.split("-")[0]
    location = location.split("or")[0]
    location = location.replace("remote", "")
    location = location.replace("hybrid", "")
    location = location.replace("in office", "")
    return location


def plan_country_fix(location, country, country_code):
    """Return {"country", "country_code"} to write, or None to leave the row alone."""
    country = (country or "").strip().lower()
    location = location or ""

    if re.fullmatch(r"[a-z]{2}", country):
        name = utils.country_from_code(country)
        return {"country": name, "country_code": country.upper()} if name else None

    if not location.strip():
        return None

    cleaned = utils.clean_location(location)
    explicit = utils._explicit_country(cleaned) if cleaned else None
    mangled = legacy_clean_location(location).strip(" ,") != cleaned
    if not explicit and not mangled:
        return None

    if not explicit and country and country in location.lower():
        # Multi-city lists ("Singapore, Chengdu"): the stored country is named in the text; keep it.
        return None

    # Never write find_country's US fallback here: only countries we positively resolved.
    proposed = explicit or utils._geocode_country(cleaned)
    if not proposed:
        return None
    if proposed["country"] == country and proposed["country_code"] == (country_code or "").upper():
        return None
    return proposed


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--apply", action="store_true", help="write changes (default: dry run)")
    parser.add_argument("--days", type=int, default=65, help="only jobs created in the last N days")
    args = parser.parse_args()

    from hetzner_utils import start_postgres_connection

    conn = start_postgres_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT job_id, location, country, country_code FROM jobs WHERE CURRENT_DATE - start_date < %s",
            (args.days,),
        )
        rows = cursor.fetchall()

    changes = []
    for job_id, location, country, country_code in rows:
        fix = plan_country_fix(location, country, country_code)
        if fix:
            changes.append((job_id, location, country, fix))
            print(f"{job_id}: {location!r}: {country} -> {fix['country']} ({fix['country_code']})")

    print(f"\n{len(changes)} of {len(rows)} jobs would change.")
    if not args.apply:
        print("Dry run only; re-run with --apply to write.")
        return

    with conn:  # one transaction: all rows update or none do
        with conn.cursor() as cursor:
            for job_id, _, _, fix in changes:
                cursor.execute(
                    "UPDATE jobs SET country = %s, country_code = %s WHERE job_id = %s",
                    (fix["country"], fix["country_code"], job_id),
                )
    print(f"Updated {len(changes)} jobs.")


if __name__ == "__main__":
    main()
