import re
from datetime import date, datetime
from urllib.parse import urlsplit, urlunsplit


LOCALE_PATH_PATTERN = re.compile(r"^/[a-z]{2}-[a-z]{2}/", re.IGNORECASE)


def canonicalize_workday_url(url: str) -> str:
    """Normalize locale and query variants of a Workday job URL."""
    parts = urlsplit(url.strip())
    path = LOCALE_PATH_PATTERN.sub("/", parts.path).rstrip("/")
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), path, "", ""))


def title_matches_keywords(title: str, keywords: list[str]) -> bool:
    for keyword in keywords:
        pattern = rf"(?<!\w){re.escape(keyword)}(?!\w)"
        if re.search(pattern, title, flags=re.IGNORECASE):
            return True
    return False


def parse_workday_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def is_active_posting(job_info: dict, *, today: date) -> bool:
    if not job_info.get("posted", True) or not job_info.get("canApply", True):
        return False

    end_date = parse_workday_date(job_info.get("endDate"))
    return end_date is None or end_date >= today
