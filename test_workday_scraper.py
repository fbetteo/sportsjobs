import unittest
from datetime import date

from hetzner_utils import get_urls_by_domain
from workday_parsing import (
    canonicalize_workday_url,
    is_active_posting,
    title_matches_keywords,
)


class FakeCursor:
    def __init__(self, records):
        self.records = records
        self.query = None
        self.params = None

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def execute(self, query, params):
        self.query = query
        self.params = params

    def fetchall(self):
        return self.records


class FakeConnection:
    def __init__(self, records):
        self.cursor_instance = FakeCursor(records)

    def cursor(self):
        return self.cursor_instance


class WorkdayParsingTests(unittest.TestCase):
    def test_canonicalizes_locale_query_and_trailing_slash(self):
        self.assertEqual(
            canonicalize_workday_url(
                "https://TENNIS.wd3.myworkdayjobs.com/en-US/ta_careers/"
                "job/Melbourne/Data-Engineer_R123/?source=LinkedIn"
            ),
            "https://tennis.wd3.myworkdayjobs.com/ta_careers/"
            "job/Melbourne/Data-Engineer_R123",
        )

    def test_title_keywords_use_word_boundaries(self):
        keywords = ["data", "engineer", "ai"]
        self.assertTrue(title_matches_keywords("Senior Data Engineer", keywords))
        self.assertTrue(title_matches_keywords("AI Enablement Manager", keywords))
        self.assertFalse(title_matches_keywords("Retail Manager", keywords))

    def test_inactive_or_expired_postings_are_rejected(self):
        today = date(2026, 9, 23)
        self.assertTrue(
            is_active_posting(
                {"posted": True, "canApply": True, "endDate": "2026-09-23"},
                today=today,
            )
        )
        self.assertFalse(
            is_active_posting(
                {"posted": True, "canApply": True, "endDate": "2026-09-22"},
                today=today,
            )
        )
        self.assertFalse(
            is_active_posting(
                {"posted": True, "canApply": False},
                today=today,
            )
        )

    def test_domain_url_lookup_is_parameterized_and_all_time(self):
        connection = FakeConnection(
            [
                ("https://tennis.wd3.myworkdayjobs.com/job/1",),
                (None,),
            ]
        )

        self.assertEqual(
            get_urls_by_domain(connection, "myworkdayjobs.com"),
            ["https://tennis.wd3.myworkdayjobs.com/job/1"],
        )
        self.assertEqual(
            connection.cursor_instance.params,
            ("%myworkdayjobs.com%",),
        )
        self.assertNotIn("myworkdayjobs.com", connection.cursor_instance.query)


if __name__ == "__main__":
    unittest.main()
