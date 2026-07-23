import unittest

from deindex_expired_jobs import build_update_notification
from hetzner_utils import get_expired_jobs


class FakeCursor:
    def __init__(self):
        self.query = ""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def execute(self, query):
        self.query = query

    def fetchall(self):
        return []


class FakeConnection:
    def __init__(self):
        self.cursor_instance = FakeCursor()

    def cursor(self, **_kwargs):
        return self.cursor_instance


class BuildUpdateNotificationTests(unittest.TestCase):
    def test_uses_canonical_slug_url_and_updated_type(self):
        notification = build_update_notification(
            {"job_id": 123, "slug": "123-data-analyst"}
        )

        self.assertEqual(
            notification,
            {
                "url": "https://www.sportsjobs.online/jobs/123-data-analyst",
                "type": "URL_UPDATED",
            },
        )

    def test_skips_jobs_without_a_slug(self):
        self.assertIsNone(build_update_notification({"job_id": 123, "slug": None}))
        self.assertIsNone(build_update_notification({"job_id": 124, "slug": "  "}))

    def test_expiration_query_uses_creation_date_and_two_calendar_months(self):
        conn = FakeConnection()

        self.assertEqual(get_expired_jobs(conn), [])
        normalized_query = " ".join(conn.cursor_instance.query.split()).lower()
        self.assertIn("creation_date", normalized_query)
        self.assertIn("interval '2 months'", normalized_query)
        self.assertNotIn("start_date", normalized_query)
        self.assertNotIn("61", normalized_query)


if __name__ == "__main__":
    unittest.main()
