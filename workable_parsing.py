import re
from urllib.parse import urlsplit, urlunsplit


def canonicalize_workable_url(url: str, account: str) -> str:
    """Return one account-specific URL for Workable short and apply links."""
    parts = urlsplit(url.strip())
    path_parts = [part for part in parts.path.split("/") if part]

    if path_parts and path_parts[-1] == "apply":
        path_parts.pop()
    if len(path_parts) == 2 and path_parts[0] == "j":
        path_parts.insert(0, account)

    path = "/" + "/".join(path_parts)
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), path, "", ""))


def title_matches_keywords(title: str, keywords: list[str]) -> bool:
    for keyword in keywords:
        pattern = rf"(?<!\w){re.escape(keyword)}(?!\w)"
        if re.search(pattern, title, flags=re.IGNORECASE):
            return True
    return False


def is_active_workable_job(job: dict) -> bool:
    state = job.get("state")
    approval_status = job.get("approvalStatus")
    return (
        state in (None, "published")
        and approval_status in (None, "approved")
        and not job.get("isInternal", False)
    )


def format_locations(locations: list[dict] | None) -> str:
    formatted_locations = []
    for location in locations or []:
        if location.get("hidden"):
            continue
        parts = [
            location.get("city"),
            location.get("region"),
            location.get("country"),
        ]
        value = ", ".join(dict.fromkeys(part for part in parts if part))
        if value and value not in formatted_locations:
            formatted_locations.append(value)
    return "; ".join(formatted_locations)
