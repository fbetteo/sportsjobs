import unittest

from workable_parsing import (
    canonicalize_workable_url,
    format_locations,
    is_active_workable_job,
    title_matches_keywords,
)


class WorkableParsingTests(unittest.TestCase):
    def test_canonicalizes_short_account_and_apply_urls(self):
        expected = "https://apply.workable.com/rapsodo/j/BEDA3A42E6"
        self.assertEqual(
            canonicalize_workable_url(
                "https://apply.workable.com/j/BEDA3A42E6?source=LinkedIn",
                "rapsodo",
            ),
            expected,
        )
        self.assertEqual(
            canonicalize_workable_url(
                "https://apply.workable.com/rapsodo/j/BEDA3A42E6/apply/",
                "rapsodo",
            ),
            expected,
        )

    def test_title_keywords_use_word_boundaries(self):
        keywords = ["data", "engineer", "ai"]
        self.assertTrue(title_matches_keywords("Senior Data & AI Engineer", keywords))
        self.assertFalse(title_matches_keywords("Retail Manager", keywords))

    def test_active_job_requires_public_approved_state(self):
        self.assertTrue(
            is_active_workable_job(
                {
                    "state": "published",
                    "approvalStatus": "approved",
                    "isInternal": False,
                }
            )
        )
        self.assertFalse(is_active_workable_job({"state": "archived"}))
        self.assertFalse(is_active_workable_job({"isInternal": True}))

    def test_formats_visible_locations_without_duplicate_parts(self):
        self.assertEqual(
            format_locations(
                [
                    {
                        "city": "Singapore",
                        "region": "Singapore",
                        "country": "Singapore",
                        "hidden": False,
                    },
                    {
                        "city": "Hidden City",
                        "country": "Turkey",
                        "hidden": True,
                    },
                ]
            ),
            "Singapore",
        )


if __name__ == "__main__":
    unittest.main()
