import io
import os
import sys
import types
import unittest
from contextlib import redirect_stdout
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from alert_matching import (
    RankedJob,
    match_job,
    normalize_values,
    select_digest_jobs,
)
from send_alerts import (
    AlertDigest,
    build_digests,
    deliver_digests,
    main,
    render_digest,
)


NOW = datetime(2026, 7, 20, 12, 0, tzinfo=timezone.utc)


def job(job_id, **overrides):
    record = {
        "job_id": job_id,
        "slug": f"{job_id}-sports-data-role",
        "name": "Sports Data Role",
        "company": "Example Sports",
        "country": "united states",
        "remote_office": "Office",
        "seniority": "Junior",
        "sport_list": "Basketball",
        "hours": "Fulltime",
        "skills": ["Python", "SQL"],
        "industry": "Sports",
        "job_area": "Analytics",
        "job_type": "Permanent",
        "creation_date": NOW - timedelta(hours=2),
        "logo_permanent_url": "https://example.com/logo.png",
    }
    record.update(overrides)
    return record


class NormalizationAndMatchingTests(unittest.TestCase):
    def test_normalizes_null_scalar_array_and_legacy_braces(self):
        self.assertEqual(normalize_values(None), set())
        self.assertEqual(normalize_values("Full-time"), {"fulltime"})
        self.assertEqual(
            normalize_values('{Fulltime,"Part time"}'),
            {"fulltime", "part time"},
        )
        self.assertEqual(normalize_values([" Python ", "python"]), {"python"})

    def test_empty_filters_are_unrestricted(self):
        result = match_job(job(1), {"country": None, "skills": []})
        self.assertEqual(result.tier, "strong")
        self.assertEqual(result.score, 1.0)

    def test_generic_football_and_legacy_hours_match_scalars(self):
        result = match_job(
            job(1, sport_list="Football - Soccer", hours="{Fulltime}"),
            {"sport_list": ["Football"], "hours": ["Full time"]},
        )
        self.assertEqual(result.tier, "strong")
        self.assertEqual(set(result.matched_categories), {"sport_list", "hours"})

    def test_global_remote_can_cross_country_when_remote_is_allowed(self):
        remote_job = job(
            1,
            country="canada",
            remote_office="Global Remote",
        )
        self.assertEqual(
            match_job(
                remote_job,
                {"country": ["united states"], "remote_office": ["Remote"]},
            ).tier,
            "strong",
        )
        self.assertEqual(
            match_job(
                remote_job,
                {"country": ["united states"], "remote_office": ["Office"]},
            ).tier,
            "none",
        )

    def test_half_preferences_is_strong_and_one_of_four_is_close(self):
        strong = match_job(
            job(1),
            {
                "seniority": ["Junior"],
                "sport_list": ["Basketball"],
                "hours": ["Part time"],
                "skills": ["R"],
            },
        )
        close = match_job(
            job(2),
            {
                "seniority": ["Junior"],
                "sport_list": ["Baseball"],
                "hours": ["Part time"],
                "skills": ["R"],
            },
        )
        self.assertEqual((strong.tier, strong.score), ("strong", 0.5))
        self.assertEqual((close.tier, close.score), ("close", 0.25))

    def test_combines_alerts_deduplicates_and_applies_limits(self):
        jobs = [job(index) for index in range(1, 20)]
        strong, close = select_digest_jobs(
            jobs,
            [
                {"seniority": ["Junior"]},
                {"seniority": ["Junior"], "sport_list": ["Baseball"], "skills": ["R"]},
            ],
        )
        self.assertEqual(len(strong), 10)
        self.assertEqual(len(close), 0)
        self.assertEqual(len({item.job["job_id"] for item in strong}), 10)

    def test_close_matches_are_limited_to_three(self):
        jobs = [job(index) for index in range(1, 10)]
        strong, close = select_digest_jobs(
            jobs,
            [
                {
                    "seniority": ["Junior"],
                    "sport_list": ["Baseball"],
                    "hours": ["Part time"],
                    "skills": ["R"],
                }
            ],
        )
        self.assertEqual(strong, [])
        self.assertEqual(len(close), 3)


class DigestTests(unittest.TestCase):
    def test_groups_alerts_by_email_and_uses_creation_date_window(self):
        alerts = [
            {"name": "Alex", "email": " Alex@example.com ", "sport_list": ["Basketball"]},
            {"name": "Alex", "email": "alex@example.com", "skills": ["Python"]},
        ]
        jobs = [
            job(1),
            job(2, creation_date=NOW - timedelta(days=2)),
        ]
        digests, _ = build_digests(
            alerts,
            [{"email": "alex@example.com", "plan": "monthly_subscription"}],
            jobs,
            NOW,
        )
        self.assertEqual(len(digests), 1)
        self.assertEqual(digests[0].email, "alex@example.com")
        self.assertEqual([item.job["job_id"] for item in digests[0].strong], [1])

    def test_weekly_alerts_only_run_on_wednesday(self):
        alerts = [{"name": "Alex", "email": "alex@example.com"}]
        monday_digests, monday_stats = build_digests(alerts, [], [job(1)], NOW)
        wednesday = NOW + timedelta(days=2)
        wednesday_job = job(1, creation_date=wednesday - timedelta(hours=1))
        wednesday_digests, _ = build_digests(alerts, [], [wednesday_job], wednesday)
        self.assertEqual(monday_digests, [])
        self.assertEqual(monday_stats["outside_schedule"], 1)
        self.assertEqual(len(wednesday_digests), 1)

    def test_renderer_uses_slug_fields_and_escapes_content(self):
        ranked = RankedJob(
            job=job(1, name="<script>alert(1)</script>", company="A&B"),
            score=1.0,
            matched_categories=("sport_list",),
        )
        html = render_digest(
            AlertDigest("alex@example.com", "A < B", "daily", [ranked], [])
        )
        self.assertIn("/jobs/1-sports-data-role?utm_source=alerts", html)
        self.assertIn("&lt;script&gt;", html)
        self.assertIn("A&amp;B", html)
        self.assertNotIn("new_job_url", html)

    def test_one_recipient_failure_does_not_stop_the_next(self):
        ranked = RankedJob(job=job(1), score=1.0, matched_categories=())
        digests = [
            AlertDigest("fail@example.com", "Fail", "daily", [ranked], []),
            AlertDigest("ok@example.com", "OK", "daily", [ranked], []),
        ]

        def send_email(payload):
            if payload["to"] == "fail@example.com":
                raise RuntimeError("provider error")
            return {"id": "sent"}

        results = deliver_digests(digests, send_email)
        self.assertEqual(results["failed"], 1)
        self.assertEqual(results["sent"], 1)

    def test_dry_run_never_calls_provider(self):
        ranked = RankedJob(job=job(1), score=1.0, matched_categories=())
        digest = AlertDigest("alex@example.com", "Alex", "daily", [ranked], [])

        def fail_if_called(_payload):
            raise AssertionError("provider should not be called")

        results = deliver_digests([digest], fail_if_called, dry_run=True)
        self.assertEqual(results["dry_run"], 1)

    def test_main_dry_run_uses_postgres_data_without_sending(self):
        class FakeConnection:
            closed = 0

            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def close(self):
                self.closed = 1

        connection = FakeConnection()
        current_job = job(1, creation_date=datetime.now(timezone.utc))

        def fake_get_table(_connection, table):
            if table == "alerts":
                return [{"name": "Alex", "email": "alex@example.com"}]
            if table == "users":
                return [
                    {
                        "email": "alex@example.com",
                        "plan": "monthly_subscription",
                    }
                ]
            raise AssertionError(f"Unexpected table: {table}")

        def fail_if_sent(_payload):
            raise AssertionError("Resend must not be called during a dry run")

        fake_resend = types.SimpleNamespace(
            Emails=types.SimpleNamespace(send=fail_if_sent),
            api_key=None,
        )
        with (
            patch.dict(os.environ, {"ALERT_DRY_RUN": "1"}),
            patch.dict(sys.modules, {"resend": fake_resend}),
            patch("send_alerts.start_postgres_connection", return_value=connection),
            patch("send_alerts.get_table", side_effect=fake_get_table),
            patch("send_alerts.get_jobs_for_alerts", return_value=[current_job]),
            redirect_stdout(io.StringIO()),
        ):
            main()

        self.assertEqual(connection.closed, 1)


if __name__ == "__main__":
    unittest.main()
