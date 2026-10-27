"""Build the SportsJobs salary report data from salaries in past US postings.

Read-only against PostgreSQL. Not part of run_scripts.sh: run it by hand to
refresh the numbers shown on the frontend's /sports-analytics-salaries page.

    poetry run python salary_report.py [path/to/sportsjobs-frontend/lib/salaryReportData.ts]

Each posting becomes one annual USD base-pay number: the midpoint of the range
written in the description, else the stored salary. Junk, non-USD, and hourly
values are dropped, reposts are removed, and employers are grouped by company.
"""

import json
import re
import sys
from datetime import date
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

from hetzner_utils import start_postgres_connection

DEFAULT_OUTPUT = Path(__file__).resolve().parent.parent / "sportsjobs-frontend" / "lib" / "salaryReportData.ts"
MIN_ANNUAL, MAX_ANNUAL = 20_000, 500_000
# Cells with fewer postings or employers are left out of the published tables.
MIN_POSTINGS, MIN_COMPANIES = 20, 5

STORED_AMOUNT = re.compile(r"(\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?\s*([kK])?")
# "$70,000 - $75,000", "$100,000.00 to $120,000.00 USD", "$145-175K", "$58-62k USD"
RANGE_IN_TEXT = re.compile(
    r"\$\s?(\d{1,3}(?:,\d{3})+|\d{2,3}(?:\.\d)?)(?:\.\d{2})?\s?([kK])?(?:\s?USD)?"
    r"\s*(?:-|–|—|to)\s*(?:USD\s?)?\$?\s?"
    r"(\d{1,3}(?:,\d{3})+|\d{2,3}(?:\.\d)?)(?:\.\d{2})?\s?([kK])?",
    re.I,
)

COMPANY_ALIASES = {
    "red sox": "Boston Red Sox",
    "la galaxy": "Los Angeles Galaxy",
    "los angeles football club (lafc)": "Los Angeles Football Club",
    "lafc": "Los Angeles Football Club",
    "nycfc": "New York City FC",
    "angel city football club": "Angel City FC",
    "chicago fire": "Chicago Fire FC",
    "national football league (nfl)": "NFL",
    "national hockey league (nhl)": "NHL",
    "nhl team jobs": "NHL",
    "major league baseball (mlb)": "MLB",
    "national basketball association (nba)": "NBA",
    "major league soccer": "MLS League Office",
    "teamworks": "Teamworks",
    "bay-fc-jobs": "Bay FC",
    "minnesota twins ⚾️ 🇺🇸": "Minnesota Twins",
    "minnesota united": "Minnesota United FC",
    "seattle sounders": "Seattle Sounders FC",
    "anaheim ducks hockey club": "Anaheim Ducks",
    "madison square garden entertainment corp.": "Madison Square Garden",
    "fanatics collectibles": "Fanatics",
    "5py us quintiles, inc.": "IQVIA",
}

TEAMS = "Teams, leagues & orgs"
BETTING = "Betting & fantasy"
TECH = "Sports tech, media & gaming"
GROUPS = [TEAMS, BETTING, TECH]

BETTING_COMPANIES = {
    "FanDuel", "DraftKings", "PrizePicks", "UnderDog Fantasy", "Sleeper", "Fliff",
    "Novig", "Kalshi", "polymarket", "The Score", "Swish Analytics", "Genius Sports",
}
TECH_COMPANIES = {
    "playstation", "Epic Games", "2k", "Whoop", "Oura", "Peloton", "Gympass",
    "Teamworks", "Catapult Sports", "Hudl", "Hawk-Eye Innovations", "Veo", "Kickoff",
    "seatgeek", "GameTime", "TicketManager", "On Location", "Fanatics", "Fubo",
    "Flosports", "Overtime", "Barstool Sports", "PlayOn! Sports", "Playfly Sports",
    "Excel Sports Management", "TourIQ Golf", "Trajektory", "Acushnet",
    "ENVE Composites", "Red Bull", "Disney", "Cox Communications",
    "Live Nation Entertainment", "AEG Presents", "Second Spectrum", "Zelus Analytics",
}
NOT_SPORTS_COMPANIES = {"Headspace", "AllTrails", "IQVIA", "gruns", "Publicis Groupe"}

JOB_AREA_LABELS = {
    "Analytics": "Analytics",
    "DS/ML/AI": "Data science / ML",
    "Data Engineer": "Data engineering",
}


def parse_stored_salary(text):
    """Annual USD from the stored salary text, or None if it is not usable."""
    s = (text or "").strip()
    if re.search(r"€|EUR|£|GBP|hour|/hr|401", s, re.I):
        return None
    amounts = [
        float(number.replace(",", "")) * (1000 if k else 1)
        for number, k in STORED_AMOUNT.findall(s)
    ]
    amounts = [a for a in amounts if a > 0]
    if not amounts:
        return None
    if len(amounts) >= 2:
        if amounts[1] < amounts[0]:
            return None
        value = (amounts[0] + amounts[1]) / 2
    else:
        value = amounts[0]
    return value if MIN_ANNUAL <= value <= MAX_ANNUAL else None


def range_from_description(description):
    """First plausible annual USD range written in the description, as (low, high)."""
    text = re.sub(r"<[^>]+>|\\", " ", description or "")
    for lo, lo_k, hi, hi_k in RANGE_IN_TEXT.findall(text):
        low, high = float(lo.replace(",", "")), float(hi.replace(",", ""))
        if hi_k:  # "$145-175K": the k covers both numbers
            high *= 1000
            if lo_k or low < 1000:
                low *= 1000
        elif lo_k:
            low *= 1000
        if MIN_ANNUAL <= low <= high <= MAX_ANNUAL:
            return low, high
    return None


def annual_usd(stored_salary, description):
    """The one number a posting contributes: description range midpoint, else stored salary."""
    desc_range = range_from_description(description)
    if desc_range:
        return sum(desc_range) / 2
    return parse_stored_salary(stored_salary)


def normalize_company(company):
    company = (company or "").strip()
    return COMPANY_ALIASES.get(company.lower(), company)


def company_group(company):
    if company in BETTING_COMPANIES:
        return BETTING
    if company in TECH_COMPANIES:
        return TECH
    if company in NOT_SPORTS_COMPANIES:
        return None
    # Every other company in the data was reviewed by hand: teams, leagues,
    # league offices, team owners, federations, and university athletics.
    # Review new employers here when refreshing the report.
    return TEAMS


def title_level(title):
    t = (title or "").lower()
    if re.search(r"\binterns?(hip)?\b", t):
        return "Intern"
    if re.search(r"\b(senior|sr\.?|lead|principal|staff|head|director|manager|vp)\b", t):
        return "Senior / lead"
    if re.search(r"\b(junior|jr\.?|associate|entry|graduate)\b", t):
        return "Junior"
    return "Mid-level"


def fetch_postings(conn):
    return pd.read_sql(
        """
        SELECT name AS title, company, job_area, remote, salary, description, creation_date
        FROM jobs
        WHERE country = 'united states' AND coalesce(trim(salary), '') <> ''
        """,
        conn,
    )


def clean_postings(raw):
    df = raw.copy()
    df["annual_usd"] = [annual_usd(s, d) for s, d in zip(df["salary"], df["description"])]
    df["company"] = df["company"].map(normalize_company)
    df["group"] = df["company"].map(company_group)
    df = df[df["annual_usd"].notna() & df["group"].notna()].copy()

    # Reposts: same company, title, and pay -> keep the latest one.
    df["repost_key"] = df["company"].str.lower() + "|" + df["title"].str.strip().str.lower()
    df = df.sort_values("creation_date").drop_duplicates(subset=["repost_key", "annual_usd"], keep="last")

    df["level"] = df["title"].map(title_level)
    df["job_area"] = df["job_area"].map(JOB_AREA_LABELS)
    df["remote"] = df["remote"].map({True: "Remote", False: "Not remote"})
    return df


def summary_rows(df, segment_column=None):
    """One row per (group, segment) with enough postings and employers to publish."""
    rows = []
    for group in GROUPS:
        group_df = df[df["group"] == group]
        segments = [("All roles", group_df)] if segment_column is None else group_df.groupby(segment_column)
        for segment, cell in segments:
            if len(cell) < MIN_POSTINGS or cell["company"].nunique() < MIN_COMPANIES:
                continue
            pay = cell["annual_usd"]
            rows.append(
                {
                    "group": group,
                    "segment": segment,
                    "postings": len(cell),
                    "companies": int(cell["company"].nunique()),
                    "p25": int(round(pay.quantile(0.25), -3)),
                    "median": int(round(pay.median(), -3)),
                    "p75": int(round(pay.quantile(0.75), -3)),
                }
            )
    return rows


def build_report(df):
    return {
        "updatedAt": date.today().isoformat(),
        "periodStart": df["creation_date"].min().date().isoformat(),
        "periodEnd": df["creation_date"].max().date().isoformat(),
        "postings": len(df),
        "companies": int(df["company"].nunique()),
        "groups": GROUPS,
        "byGroup": summary_rows(df),
        "byGroupJobArea": summary_rows(df.dropna(subset=["job_area"]), "job_area"),
        "byGroupLevel": summary_rows(df[df["level"].isin(["Mid-level", "Senior / lead"])], "level"),
        "byGroupRemote": summary_rows(df, "remote"),
    }


def to_typescript(report):
    return (
        "// Generated by salary_report.py in the scraper repo. Do not edit by hand;\n"
        "// re-run that script to refresh the numbers.\n\n"
        "export type SalaryReportRow = {\n"
        "    group: string;\n"
        "    segment: string;\n"
        "    postings: number;\n"
        "    companies: number;\n"
        "    p25: number;\n"
        "    median: number;\n"
        "    p75: number;\n"
        "};\n\n"
        f"export const salaryReport = {json.dumps(report, indent=4, ensure_ascii=False)} as const;\n"
    )


def main():
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUTPUT
    load_dotenv()
    conn = start_postgres_connection()
    try:
        raw = fetch_postings(conn)
    finally:
        conn.close()

    df = clean_postings(raw)
    report = build_report(df)
    print(f"US postings with salary text: {len(raw)}, used: {report['postings']}, companies: {report['companies']}")
    for row in report["byGroup"]:
        print(f"  {row['group']}: median {row['median']:,.0f} ({row['postings']} postings, {row['companies']} companies)")

    unknown = sorted(set(df.loc[df["group"] == TEAMS, "company"]))
    print(f"\nGrouped as '{TEAMS}' by default ({len(unknown)}); check new names:\n  " + "; ".join(unknown))

    output.write_text(to_typescript(report), encoding="utf-8")
    print(f"\nWrote {output}")


if __name__ == "__main__":
    main()
