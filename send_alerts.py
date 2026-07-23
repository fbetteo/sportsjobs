import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from html import escape
from typing import Any, Callable, Mapping, Sequence
from urllib.parse import quote, urlencode

from alert_matching import RankedJob, select_digest_jobs
from hetzner_utils import get_jobs_for_alerts, get_table, start_postgres_connection


PAID_PLANS = {
    "lifetime",
    "yearly_subscription",
    "monthly_subscription",
    "weekly_subscription",
}
SITE_URL = "https://www.sportsjobs.online"


@dataclass(frozen=True)
class AlertDigest:
    email: str
    name: str
    frequency: str
    strong: Sequence[RankedJob]
    close: Sequence[RankedJob]


def normalize_email(value: Any) -> str:
    return str(value or "").strip().casefold()


def _parse_datetime(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
    else:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _paid_emails(users: Sequence[Mapping[str, Any]]) -> set[str]:
    return {
        normalize_email(user.get("email"))
        for user in users
        if normalize_email(user.get("email"))
        and str(user.get("plan") or "").casefold() in PAID_PLANS
    }


def _group_alerts(
    alerts: Sequence[Mapping[str, Any]],
) -> dict[str, list[Mapping[str, Any]]]:
    grouped: dict[str, list[Mapping[str, Any]]] = {}
    for alert in alerts:
        email = normalize_email(alert.get("email"))
        if email:
            grouped.setdefault(email, []).append(alert)
    return grouped


def build_digests(
    alerts: Sequence[Mapping[str, Any]],
    users: Sequence[Mapping[str, Any]],
    jobs: Sequence[Mapping[str, Any]],
    now: datetime,
) -> tuple[list[AlertDigest], dict[str, int]]:
    now = now.astimezone(timezone.utc)
    paid_emails = _paid_emails(users)
    grouped_alerts = _group_alerts(alerts)
    stats = {
        "alerts": len(alerts),
        "recipients": len(grouped_alerts),
        "skipped_digests": 0,
        "outside_schedule": 0,
        "without_matches": 0,
        "strong_matches": 0,
        "close_matches": 0,
        "jobs_without_slugs": sum(
            1 for job in jobs if not str(job.get("slug") or "").strip()
        ),
    }
    digests: list[AlertDigest] = []

    for email, user_alerts in grouped_alerts.items():
        frequency = "daily" if email in paid_emails else "weekly"
        if frequency == "weekly" and now.strftime("%A") != "Wednesday":
            stats["skipped_digests"] += 1
            stats["outside_schedule"] += 1
            continue

        window = timedelta(days=1 if frequency == "daily" else 7)
        cutoff = now - window
        eligible_jobs = [
            job
            for job in jobs
            if (created := _parse_datetime(job.get("creation_date"))) is not None
            and created >= cutoff
        ]
        strong, close = select_digest_jobs(eligible_jobs, user_alerts)
        if not strong and not close:
            stats["skipped_digests"] += 1
            stats["without_matches"] += 1
            continue

        stats["strong_matches"] += len(strong)
        stats["close_matches"] += len(close)

        first_alert = user_alerts[0]
        digests.append(
            AlertDigest(
                email=email,
                name=str(first_alert.get("name") or "there").strip() or "there",
                frequency=frequency,
                strong=strong,
                close=close,
            )
        )

    return digests, stats


def _job_url(job: Mapping[str, Any], frequency: str) -> str:
    slug = quote(str(job.get("slug") or "").strip(), safe="-")
    query = urlencode(
        {
            "utm_source": "alerts",
            "utm_medium": "email",
            "utm_campaign": f"{frequency}_job_alert",
        }
    )
    return f"{SITE_URL}/jobs/{slug}?{query}"


def _render_jobs(jobs: Sequence[RankedJob], frequency: str) -> str:
    rows: list[str] = []
    for ranked in jobs:
        job = ranked.job
        title = escape(str(job.get("name") or "Sports job"))
        company = escape(str(job.get("company") or ""))
        country = escape(str(job.get("country") or ""))
        logo_url = escape(str(job.get("logo_permanent_url") or ""), quote=True)
        image = (
            f'<img src="{logo_url}" alt="" width="64" '
            'style="display:block;max-height:64px;object-fit:contain;">'
            if logo_url
            else ""
        )
        details = " · ".join(part for part in (company, country) if part)
        rows.append(
            f"""
            <tr>
              <td style="padding:12px;border-bottom:1px solid #ddd;width:72px;">{image}</td>
              <td style="padding:12px;border-bottom:1px solid #ddd;text-align:left;">
                <a href="{escape(_job_url(job, frequency), quote=True)}" style="color:#0066cc;text-decoration:none;font-weight:bold;">{title}</a>
                <div style="color:#555;margin-top:4px;">{details}</div>
              </td>
            </tr>
            """
        )
    return '<table style="width:100%;border-collapse:collapse;">' + "".join(rows) + "</table>"


def render_digest(digest: AlertDigest) -> str:
    period = "today" if digest.frequency == "daily" else "this week"
    sections = [
        f"<h2 style=\"color:#0066cc;\">Hi {escape(digest.name)}</h2>",
        f"<p>Here are the strongest new job matches we found {period}.</p>",
    ]
    if digest.strong:
        sections.append(_render_jobs(digest.strong, digest.frequency))
    if digest.close:
        sections.extend(
            [
                '<h3 style="color:#3d1f89;margin-top:28px;">Close matches</h3>',
                "<p>These satisfy your location and work-mode choices and match some of your other preferences.</p>",
                _render_jobs(digest.close, digest.frequency),
            ]
        )
    if digest.frequency == "weekly":
        sections.append(
            '<p style="margin-top:28px;"><a href="https://www.sportsjobs.online/signup?utm_source=alerts&amp;utm_medium=email&amp;utm_campaign=weekly_alert_upgrade">Upgrade for daily alerts</a></p>'
        )
    return (
        '<body style="font-family:Arial,sans-serif;margin:0;padding:20px;color:#333;">'
        '<div style="max-width:640px;margin:auto;padding:24px;border:1px solid #ddd;border-radius:8px;background:#f9f9f9;">'
        '<h1 style="color:#0066cc;">SportsJobs Online</h1>'
        + "".join(sections)
        + "</div></body>"
    )


def deliver_digests(
    digests: Sequence[AlertDigest],
    send_email: Callable[[dict[str, Any]], Any],
    dry_run: bool = False,
) -> dict[str, int]:
    results = {"prepared": len(digests), "sent": 0, "failed": 0, "dry_run": 0}
    for digest in digests:
        payload = {
            "from": "noreply@alerts.sportsjobs.online",
            "to": digest.email,
            "subject": (
                "Your daily SportsJobs matches"
                if digest.frequency == "daily"
                else "Your weekly SportsJobs matches"
            ),
            "html": render_digest(digest),
        }
        if dry_run:
            results["dry_run"] += 1
            print(
                json.dumps(
                    {
                        "event": "alert_digest_dry_run",
                        "email": digest.email,
                        "strong": len(digest.strong),
                        "close": len(digest.close),
                    }
                )
            )
            continue
        try:
            response = send_email(payload)
            results["sent"] += 1
            resend_id = (
                response.get("id")
                if isinstance(response, Mapping)
                else getattr(response, "id", None)
            )
            print(
                json.dumps(
                    {
                        "event": "alert_digest_sent",
                        "email": digest.email,
                        "strong": len(digest.strong),
                        "close": len(digest.close),
                        "resend_id": resend_id,
                    },
                    default=str,
                )
            )
        except Exception as error:
            results["failed"] += 1
            print(
                json.dumps(
                    {
                        "event": "alert_digest_failed",
                        "email": digest.email,
                        "error": str(error),
                    }
                )
            )
    return results


def _env_flag(name: str) -> bool:
    return os.getenv(name, "").strip().casefold() in {"1", "true", "yes", "on"}


def main() -> None:
    dry_run = _env_flag("ALERT_DRY_RUN")
    now = datetime.now(timezone.utc)
    conn = start_postgres_connection()
    try:
        with conn:
            alerts = get_table(conn, "alerts")
            users = get_table(conn, "users")
            jobs = get_jobs_for_alerts(conn, now - timedelta(days=7))

        digests, matching_stats = build_digests(alerts, users, jobs, now)
        if dry_run:
            send_email = lambda _payload: None
        else:
            import resend

            resend.api_key = os.environ["RESEND_API_KEY"]
            send_email = resend.Emails.send
        delivery_stats = deliver_digests(digests, send_email, dry_run=dry_run)
        print(
            json.dumps(
                {
                    "event": "alert_run_complete",
                    **matching_stats,
                    **delivery_stats,
                }
            )
        )
    except Exception as error:
        print(json.dumps({"event": "alert_run_failed", "error": str(error)}))
        raise
    finally:
        if conn and conn.closed == 0:
            conn.close()
            print("Connection closed.")


if __name__ == "__main__":
    main()
