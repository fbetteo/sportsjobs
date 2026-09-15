import io
import json
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

    def test_country_and_work_mode_are_both_required(self):
        remote_job = job(
            1,
            country="canada",
            remote_office="Global Remote",
        )
        self.assertEqual(
            match_job(
                remote_job,
                {"country": ["canada", "united states"], "remote_office": ["Remote"]},
            ).tier,
            "strong",
        )
        self.assertEqual(
            match_job(remote_job, {"country": ["united states"]}).tier,
            "none",
        )
        self.assertEqual(
            match_job(
                remote_job,
                {"country": ["united states"], "remote_office": ["Office"]},
            ).tier,
            "none",
        )

    def test_any_value_within_each_filter_matches_but_every_filter_is_required(self):
        alert = {
            "country": ["canada", "united states"],
            "seniority": ["Internship"],
            "remote_office": ["Remote"],
            "sport_list": ["Baseball", "Basketball"],
        }
        result = match_job(job(1, seniority="Internship", remote_office="Remote"), alert)
        self.assertEqual(result.tier, "strong")
        self.assertEqual(result.score, 1.0)
        self.assertEqual(set(result.matched_categories), {"country", "seniority", "remote_office", "sport_list"})
        self.assertEqual(match_job(job(2, country="canada", seniority="Internship", remote_office="Remote", sport_list="Baseball"), alert).tier, "strong")
        self.assertEqual(match_job(job(3, seniority="Junior", remote_office="Remote"), alert).tier, "none")
        self.assertEqual(match_job(job(4, country="spain", seniority="Internship", remote_office="Remote"), alert).tier, "none")
        self.assertEqual(match_job(job(5, seniority="Internship", remote_office="Office"), alert).tier, "none")
        self.assertEqual(match_job(job(6, seniority="Internship", remote_office="Remote", sport_list="Tennis"), alert).tier, "none")

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

    def test_old_extra_filters_are_also_required(self):
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
        self.assertEqual(close, [])


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
            [{"email": "alex@example.com", "auth0_sub": "auth0|alex", "plan": "free"}],
            jobs,
            NOW,
        )
        self.assertEqual(len(digests), 1)
        self.assertEqual(digests[0].email, "alex@example.com")
        self.assertEqual([item.job["job_id"] for item in digests[0].strong], [1])

    def test_only_logged_in_users_receive_alerts(self):
        alerts = [{"name": "Alex", "email": "alex@example.com"}]
        pre_auth_digests, _ = build_digests(alerts, [], [job(1)], NOW)
        logged_in_digests, _ = build_digests(
            alerts,
            [{"email": "alex@example.com", "auth0_sub": "auth0|alex", "plan": "free", "subscription_status": "none"}],
            [job(1)], NOW,
        )
        self.assertEqual(pre_auth_digests, [])
        self.assertEqual(len(logged_in_digests), 1)

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
        self.assertIn('href="https://www.sportsjobs.online/settings"', html)
        self.assertIn("Manage your job alerts", html)
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

    def test_response_without_email_id_is_a_failure_and_next_digest_is_sent(self):
        ranked = RankedJob(job=job(1), score=1.0, matched_categories=())
        digests = [
            AlertDigest("first@example.com", "First", "daily", [ranked], []),
            AlertDigest("second@example.com", "Second", "daily", [ranked], []),
        ]
        responses = iter([{}, {"id": "email_123"}])
        output = io.StringIO()

        with redirect_stdout(output):
            results = deliver_digests(digests, lambda _payload: next(responses))

        events = [json.loads(line) for line in output.getvalue().splitlines()]
        self.assertEqual(results, {"prepared": 2, "sent": 1, "failed": 1, "dry_run": 0})
        self.assertEqual(events[0]["reason"], "missing_resend_id")
        self.assertEqual(events[1]["resend_id"], "email_123")
        self.assertNotIn("first@example.com", output.getvalue())

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
                        "auth0_sub": "auth0|alex",
                        "plan": "free",
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

    def test_main_reports_partial_send_failure_and_exits_unsuccessfully(self):
        class FakeConnection:
            closed = 0

            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def close(self):
                self.closed = 1

        connection = FakeConnection()
        ranked = RankedJob(job=job(1), score=1.0, matched_categories=())
        digest = AlertDigest("alex@example.com", "Alex", "daily", [ranked], [])
        fake_resend = types.SimpleNamespace(
            Emails=types.SimpleNamespace(send=lambda _payload: {}),
            api_key=None,
        )
        output = io.StringIO()

        with (
            patch.dict(os.environ, {"ALERT_DRY_RUN": "0", "RESEND_API_KEY": "test"}),
            patch.dict(sys.modules, {"resend": fake_resend}),
            patch("send_alerts.start_postgres_connection", return_value=connection),
            patch("send_alerts.get_table", return_value=[]),
            patch("send_alerts.get_jobs_for_alerts", return_value=[]),
            patch("send_alerts.build_digests", return_value=([digest], {"recipients": 1})),
            redirect_stdout(output),
        ):
            with self.assertRaisesRegex(RuntimeError, "1 alert digest\\(s\\) failed"):
                main()

        events = [json.loads(line) for line in output.getvalue().splitlines() if line.startswith("{")]
        self.assertEqual(events[-1]["event"], "alert_run_failed")
        self.assertEqual(events[-1]["failed"], 1)
        self.assertEqual(events[-1]["sent"], 0)
        self.assertEqual(connection.closed, 1)


if __name__ == "__main__":
    unittest.main()
