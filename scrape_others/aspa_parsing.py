import re
from datetime import date, datetime
from urllib.parse import urlsplit, urlunsplit


ASPA_COMPANY_FALLBACK = "TheASPA"


def canonicalize_job_url(url: str) -> str:
    """Remove category/query data so one ASPA post has one database URL."""
    parts = urlsplit(url.strip())
    return urlunsplit((parts.scheme, parts.netloc, parts.path.rstrip("/"), "", ""))


def parse_published_date(value: str) -> date | None:
    try:
        return datetime.strptime(value.strip(), "%d %B %Y").date()
    except (TypeError, ValueError):
        return None


def is_recent_post(
    published_date: str,
    *,
    today: date,
    max_age_days: int,
) -> bool:
    parsed_date = parse_published_date(published_date)
    if parsed_date is None:
        return False

    age_in_days = (today - parsed_date).days
    return 0 <= age_in_days <= max_age_days


def extract_closing_date(text: str) -> date | None:
    label_pattern = r"(?:applications?\s+close|closing\s+date|closing|close)\s*:?[\s\u00a0]*"
    date_pattern = r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{1,2}\s+[A-Za-z]+\s+\d{4})"
    match = re.search(label_pattern + date_pattern, text, flags=re.IGNORECASE)
    if not match:
        return None

    value = match.group(1)
    for date_format in (
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%d/%m/%y",
        "%d-%m-%y",
        "%d %B %Y",
        "%d %b %Y",
    ):
        try:
            return datetime.strptime(value, date_format).date()
        except ValueError:
            continue
    return None


def has_closed(text: str, *, today: date) -> bool:
    closing_date = extract_closing_date(text)
    return closing_date is not None and closing_date < today


def split_title_and_company(title: str) -> tuple[str, str]:
    cleaned_title = title.strip()
    if "|" not in cleaned_title:
        return cleaned_title, ASPA_COMPANY_FALLBACK

    role, company = cleaned_title.rsplit("|", 1)
    role = role.strip()
    company = company.strip()
    if not role or not company:
        return cleaned_title, ASPA_COMPANY_FALLBACK
    return role, company


def extract_location(text: str) -> str:
    if not text:
        return ""

    location = ""
    if "📍" in text:
        location = text.split("📍", 1)[1]
        stop_markers = (
            "📄",
            "📊",
            "💰",
            "📅",
            "🕒",
            "🕑",
            "🚫",
            "🏀",
            "⚽",
            "🏏",
            "🎓",
            "|",
        )
        stop_positions = [
            location.find(marker) for marker in stop_markers if marker in location
        ]
        if stop_positions:
            location = location[: min(stop_positions)]
    else:
        match = re.search(
            r"\b(?:location)\s*[-:]\s*([^\n]+)",
            text,
            flags=re.IGNORECASE,
        )
        if match:
            location = match.group(1)

    # Remove country-flag regional indicator characters before geocoding.
    location = re.sub(r"[\U0001F1E6-\U0001F1FF]", "", location)
    return re.sub(r"\s+", " ", location).strip(" ,-")
