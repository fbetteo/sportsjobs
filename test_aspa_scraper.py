import unittest
from datetime import date

from scrape_others.aspa_parsing import (
    canonicalize_job_url,
    extract_closing_date,
    extract_location,
    has_closed,
    is_recent_post,
    split_title_and_company,
)


TODAY = date(2026, 9, 22)


class ASPAParsingTests(unittest.TestCase):
    def test_canonical_url_removes_category_query_and_fragment(self):
        self.assertEqual(
            canonicalize_job_url(
                "https://theaspa.org/jobs-board/f/data-scientist"
                "?blogcategory=Data+Scientist#details"
            ),
            "https://theaspa.org/jobs-board/f/data-scientist",
        )

    def test_recent_window_is_inclusive_and_rejects_invalid_dates(self):
        self.assertTrue(
            is_recent_post("15 September 2026", today=TODAY, max_age_days=7)
        )
        self.assertTrue(
            is_recent_post("22 September 2026", today=TODAY, max_age_days=7)
        )
        self.assertFalse(
            is_recent_post("14 September 2026", today=TODAY, max_age_days=7)
        )
        self.assertFalse(is_recent_post("unknown", today=TODAY, max_age_days=7))

    def test_extracts_common_closing_date_formats(self):
        self.assertEqual(
            extract_closing_date("Closing: 25 September 2026, 12:00"),
            date(2026, 9, 25),
        )
        self.assertEqual(
            extract_closing_date("Applications close: 10/09/2026"),
            date(2026, 9, 10),
        )
        self.assertEqual(
            extract_closing_date("Close 20/09/2026"),
            date(2026, 9, 20),
        )
        self.assertTrue(has_closed("Close: 20/09/2026", today=TODAY))
        self.assertFalse(has_closed("Close: 22/09/2026", today=TODAY))

    def test_splits_role_and_company_at_last_separator(self):
        self.assertEqual(
            split_title_and_company(
                "Data Scientist, Basketball Operations | Los Angeles Sparks"
            ),
            ("Data Scientist, Basketball Operations", "Los Angeles Sparks"),
        )
        self.assertEqual(
            split_title_and_company("Data Scientist"),
            ("Data Scientist", "TheASPA"),
        )

    def test_extracts_location_from_listing_summary(self):
        self.assertEqual(
            extract_location(
                "🌐 Rowing Australia 📍 Canberra, ACT, Australia 🇦🇺 | Hybrid 🕒 Full-Time"
            ),
            "Canberra, ACT, Australia",
        )
        self.assertEqual(
            extract_location("📍 Manchester, UK 📊 Performance Data Analyst"),
            "Manchester, UK",
        )
        self.assertEqual(
            extract_location("LOCATION - Loughborough (UK)\nQualification Type: PhD"),
            "Loughborough (UK)",
        )


if __name__ == "__main__":
    unittest.main()
