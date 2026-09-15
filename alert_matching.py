import csv
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping, Sequence


ALERT_FILTERS = (
    ("country", "country"),
    ("remote_office", "remote_office"),
    ("seniority", "seniority"),
    ("sport_list", "sport_list"),
    ("hours", "hours"),
    ("skills", "skills"),
    ("industry", "industry"),
    ("job_area", "job_area"),
    ("type", "job_type"),
)

VALUE_ALIASES = {
    "full time": "fulltime",
    "full-time": "fulltime",
    "part-time": "part time",
}


@dataclass(frozen=True)
class MatchResult:
    tier: str
    score: float
    matched_categories: tuple[str, ...]
    preference_categories: int


@dataclass(frozen=True)
class RankedJob:
    job: Mapping[str, Any]
    score: float
    matched_categories: tuple[str, ...]


def _is_missing(value: Any) -> bool:
    return value is None or (
        isinstance(value, float) and math.isnan(value)
    )


def _split_scalar(value: str) -> list[str]:
    value = value.strip()
    if value.startswith("{") and value.endswith("}"):
        inner = value[1:-1]
        if not inner:
            return []
        return next(csv.reader([inner], skipinitialspace=True))
    return [value]


def normalize_values(value: Any) -> set[str]:
    """Normalize PostgreSQL arrays, scalars, and legacy brace-formatted values."""
    if _is_missing(value):
        return set()

    if isinstance(value, str):
        raw_values: Iterable[Any] = _split_scalar(value)
    elif isinstance(value, (list, tuple, set)):
        raw_values = value
    else:
        raw_values = [value]

    normalized: set[str] = set()
    for raw_value in raw_values:
        if _is_missing(raw_value):
            continue
        if isinstance(raw_value, (list, tuple, set)):
            normalized.update(normalize_values(raw_value))
            continue
        token = str(raw_value).strip().strip('"').strip("'").casefold()
        if token:
            normalized.add(VALUE_ALIASES.get(token, token))
    return normalized


def normalize_field_values(field: str, value: Any) -> set[str]:
    values = normalize_values(value)
    if field == "sport_list":
        if "football" in values:
            values.update({"football - nfl", "football - soccer"})
        if "nfl" in values:
            values.add("football - nfl")
        if "soccer" in values:
            values.add("football - soccer")
    return values


def match_job(job: Mapping[str, Any], alert: Mapping[str, Any]) -> MatchResult:
    selected_categories = 0
    matched_categories: list[str] = []
    for alert_field, job_field in ALERT_FILTERS:
        selected = normalize_field_values(alert_field, alert.get(alert_field))
        if not selected:
            continue
        selected_categories += 1
        if alert_field == "remote_office" and "remote" in selected:
            selected.add("global remote")
        job_values = normalize_field_values(alert_field, job.get(job_field))
        if not selected & job_values:
            return MatchResult("none", 0.0, tuple(matched_categories), selected_categories)
        matched_categories.append(alert_field)

    if selected_categories == 0:
        return MatchResult("strong", 1.0, (), 0)

    return MatchResult("strong", 1.0, tuple(matched_categories), selected_categories)


def _job_key(job: Mapping[str, Any]) -> str:
    return str(job.get("job_id") or job.get("slug") or job.get("url") or "")


def _creation_timestamp(job: Mapping[str, Any]) -> float:
    value = job.get("creation_date")
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return 0.0
    else:
        return 0.0
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.timestamp()


def _numeric_job_id(job: Mapping[str, Any]) -> int:
    try:
        return int(job.get("job_id") or 0)
    except (TypeError, ValueError):
        return 0


def select_digest_jobs(
    jobs: Sequence[Mapping[str, Any]],
    alerts: Sequence[Mapping[str, Any]],
    strong_limit: int = 10,
    close_limit: int = 3,
) -> tuple[list[RankedJob], list[RankedJob]]:
    """Rank and deduplicate jobs across every alert owned by one email."""
    best_by_job: dict[str, RankedJob] = {}
    tier_by_job: dict[str, str] = {}

    for job in jobs:
        key = _job_key(job)
        if not key or not str(job.get("slug") or "").strip():
            continue

        for alert in alerts:
            result = match_job(job, alert)
            if result.tier == "none":
                continue

            existing = best_by_job.get(key)
            existing_tier = tier_by_job.get(key)
            should_replace = (
                existing is None
                or (result.tier == "strong" and existing_tier != "strong")
                or (
                    result.tier == existing_tier
                    and result.score > existing.score
                )
            )
            if should_replace:
                best_by_job[key] = RankedJob(
                    job=job,
                    score=result.score,
                    matched_categories=result.matched_categories,
                )
                tier_by_job[key] = result.tier

    def sort_key(ranked: RankedJob) -> tuple[float, float, int]:
        return (
            ranked.score,
            _creation_timestamp(ranked.job),
            _numeric_job_id(ranked.job),
        )

    strong = sorted(
        (
            ranked
            for key, ranked in best_by_job.items()
            if tier_by_job[key] == "strong"
        ),
        key=sort_key,
        reverse=True,
    )[:strong_limit]
    close = sorted(
        (
            ranked
            for key, ranked in best_by_job.items()
            if tier_by_job[key] == "close"
        ),
        key=sort_key,
        reverse=True,
    )[:close_limit]
    return strong, close
