import os
import unittest
from unittest import mock

# utils builds an Airtable table handle at import time; tests never call Airtable.
os.environ.setdefault("AIRTABLE_TOKEN", "test")
os.environ.setdefault("AIRTABLE_BASE", "appTest")
os.environ.setdefault("AIRTABLE_JOBS_TABLE", "jobs")

import utils  # noqa: E402


class CleanLocationTests(unittest.TestCase):
    def test_keeps_words_containing_separator_letters(self):
        # Regression: substring splits produced "baltim" (Egypt) and "atlanta, ge" (Indonesia).
        self.assertEqual(utils.clean_location("Baltimore, MD"), "baltimore, md")
        self.assertEqual(utils.clean_location("Atlanta, Georgia, United States"), "atlanta, georgia, united states")
        self.assertEqual(utils.clean_location("Stoke-on-Trent, England"), "stoke-on-trent, england")

    def test_takes_first_real_alternative(self):
        self.assertEqual(utils.clean_location("London / Remote"), "london")
        self.assertEqual(utils.clean_location("New York or Boston"), "new york")
        self.assertEqual(utils.clean_location("Remote - US"), "us")
        self.assertEqual(utils.clean_location("Liberty Corner, NJ · Hybrid"), "liberty corner, nj")

    def test_middle_dot_separates_city_and_state(self):
        # Regression: splitting on "·" sent "St. Petersburg · FL" (Tampa Bay Rays) to Russia.
        self.assertEqual(utils.clean_location("St. Petersburg · FL"), "st. petersburg, fl")

    def test_oregon_after_comma_is_not_a_separator(self):
        self.assertEqual(utils.clean_location("Portland, OR"), "portland, or")

    def test_only_noise_is_empty(self):
        self.assertEqual(utils.clean_location("Remote"), "")


class FindCountryTests(unittest.TestCase):
    def setUp(self):
        patcher = mock.patch.object(utils, "_geocode_country", return_value=None)
        self.geocode = patcher.start()
        self.addCleanup(patcher.stop)

    def test_explicit_country_skips_geocoder(self):
        cases = {
            "Vancouver, BC V6B0N8, CAN": "canada",
            "Manchester, England, United Kingdom": "united kingdom",
            "UK": "united kingdom",
            "UK Based, with travel": "united kingdom",
            "Concord, NC": "united states",
            "Baltimore, MD": "united states",
            "Remote - US": "united states",
            "St. Petersburg · FL": "united states",
            "Voorhees Township · NJ": "united states",
        }
        for location, country in cases.items():
            with self.subTest(location=location):
                self.assertEqual(utils.find_country(location)["country"], country)
        self.geocode.assert_not_called()

    def test_ambiguous_codes_go_to_geocoder(self):
        self.geocode.return_value = {"country": "germany", "country_code": "DE"}
        self.assertEqual(utils.find_country("Berlin, DE"), {"country": "germany", "country_code": "DE"})
        self.geocode.assert_called_once_with("berlin, de")

    def test_always_returns_dict_with_logged_default(self):
        for location in ["Somewhere unknown", "", None, "Remote"]:
            with self.subTest(location=location):
                self.assertEqual(utils.find_country(location), {"country": "united states", "country_code": "US"})


class GeocodeCacheTests(unittest.TestCase):
    def setUp(self):
        utils._country_cache.clear()
        self.addCleanup(utils._country_cache.clear)

    def test_successful_lookup_is_cached(self):
        location = mock.Mock(raw={"address": {"country": "Croatia", "country_code": "hr"}})
        with mock.patch.object(utils, "_geocode", return_value=location) as geocode:
            self.assertEqual(utils.country_from_code("HR"), "croatia")
            self.assertEqual(utils.country_from_code("hr"), "croatia")
        geocode.assert_called_once()

    def test_errors_are_not_cached(self):
        location = mock.Mock(raw={"address": {"country": "Spain", "country_code": "es"}})
        with mock.patch.object(utils, "_geocode", side_effect=[TimeoutError("slow"), location]):
            self.assertIsNone(utils._geocode_country("madrid"))
            self.assertEqual(utils._geocode_country("madrid"), {"country": "spain", "country_code": "ES"})


if __name__ == "__main__":
    unittest.main()
