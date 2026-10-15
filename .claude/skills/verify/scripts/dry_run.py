"""Run one SportsJobs pipeline script with PostgreSQL replaced by an in-memory fake.

The script runs unchanged against the real job sites, Airtable schema and geocoder,
but every `hetzner_utils.insert_records` call is captured to a JSON file instead of
being written, and the duplicate-URL/skills reads return empty lists.

Usage (from the repo root):
    poetry run python .claude/skills/verify/scripts/dry_run.py --doctor
    poetry run python .claude/skills/verify/scripts/dry_run.py workable_scraper.py
"""

import argparse
import json
import os
import runpy
import sys
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
EVIDENCE_DIR = REPO / ".verify-evidence"
REQUIRED_ENV = ["AIRTABLE_TOKEN", "AIRTABLE_BASE", "AIRTABLE_JOBS_TABLE"]


class FakeConnection:
    closed = 0

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def close(self):
        self.closed = 1

    def rollback(self):
        pass

    def cursor(self):
        raise RuntimeError("dry run: raw SQL is not stubbed; extend FakeConnection")


class Tee:
    def __init__(self, *streams):
        self.streams = streams

    def write(self, text):
        for stream in self.streams:
            stream.write(text)

    def flush(self):
        for stream in self.streams:
            stream.flush()


def stub_database(captured):
    import psycopg2
    import hetzner_utils

    def refuse_connect(*args, **kwargs):
        raise RuntimeError("dry run: real PostgreSQL connection attempted")

    def capture_insert(conn, table, data):
        captured.append({"table": table, "data": data})
        print(f"[dry run] captured insert into {table}: {data.get('name')} {data.get('url')}")

    psycopg2.connect = refuse_connect
    hetzner_utils.start_postgres_connection = FakeConnection
    hetzner_utils.get_recent_urls = lambda conn, days=65: []
    hetzner_utils.get_urls_by_domain = lambda conn, domain: []
    hetzner_utils.get_skills = lambda conn: []
    hetzner_utils.insert_records = capture_insert


def doctor():
    ok = True
    print(f"python {sys.version.split()[0]} at {sys.executable}")
    if not (REPO / ".env").exists():
        print("FAIL .env missing at repo root")
        return False
    missing = [name for name in REQUIRED_ENV if not os.getenv(name)]
    if missing:
        print(f"FAIL env vars missing: {', '.join(missing)}")
        ok = False
    try:
        import markdownify, selenium, geopy, pyairtable  # noqa: F401
        print("ok   scraper dependencies import")
    except ImportError as error:
        print(f"FAIL dependency import: {error}")
        ok = False
    if ok:
        import utils

        fields = [field.name for field in utils.table.schema().fields]
        if "skills" in fields:
            print("ok   Airtable jobs schema readable (skills field present)")
        else:
            print("FAIL Airtable jobs schema has no skills field")
            ok = False
    print("READY" if ok else "NOT READY")
    return ok


def run(script):
    script_path = (REPO / script).resolve()
    if not script_path.is_file():
        sys.exit(f"no such script: {script}")

    EVIDENCE_DIR.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    base = EVIDENCE_DIR / f"{stamp}-{script_path.stem}"
    captured = []
    stub_database(captured)

    sys.argv = [str(script_path)]
    sys.path.insert(0, str(script_path.parent))
    exit_code = 0
    with open(f"{base}.log", "w", encoding="utf-8") as log:
        real_stdout = sys.stdout
        sys.stdout = Tee(real_stdout, log)
        try:
            runpy.run_path(str(script_path), run_name="__main__")
        except SystemExit as error:
            exit_code = error.code if isinstance(error.code, int) else 1
        finally:
            sys.stdout = real_stdout

    Path(f"{base}.json").write_text(
        json.dumps(
            {"script": script, "exit_code": exit_code, "inserts": captured},
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )
    print(f"\n[dry run] exit code {exit_code}, {len(captured)} captured inserts")
    print(f"[dry run] evidence: {base}.json and {base}.log")
    return exit_code


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("script", nargs="?", help="repo-relative script path")
    parser.add_argument("--doctor", action="store_true")
    args = parser.parse_args()

    os.chdir(REPO)
    sys.path.insert(0, str(REPO))
    from dotenv import load_dotenv

    load_dotenv(REPO / ".env")

    if args.doctor:
        sys.exit(0 if doctor() else 1)
    if not args.script:
        parser.error("give a script path or --doctor")
    sys.exit(run(args.script))


if __name__ == "__main__":
    main()
