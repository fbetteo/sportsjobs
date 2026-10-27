import unittest

from salary_report import annual_usd, company_group, range_from_description, title_level


class RangeFromDescriptionTest(unittest.TestCase):
    def test_reads_common_range_formats(self):
        cases = {
            "The salary range is $70,000 - $75,000 per year.": (70_000, 75_000),
            "Pay: $100,000.00 to $120,000.00 USD": (100_000, 120_000),
            "Salary: $145-175K": (145_000, 175_000),
            "**Pay Range:** $58\\-62k USD.": (58_000, 62_000),
            "Base salary: $100,000\\-190,000 (encompasses multiple levels)": (100_000, 190_000),
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                self.assertEqual(range_from_description(text), expected)

    def test_ignores_hourly_and_implausible_ranges(self):
        self.assertIsNone(range_from_description("We pay $25 - $35 per hour."))
        self.assertIsNone(range_from_description("Raised $10,000,000 - $20,000,000 in funding."))


class AnnualUsdTest(unittest.TestCase):
    def test_prefers_description_range_midpoint_over_stored_minimum(self):
        self.assertEqual(annual_usd("$120,000", "Pay scale: $120,000 - $130,000"), 125_000)

    def test_falls_back_to_stored_salary(self):
        self.assertEqual(annual_usd("170k USD", "No pay in text."), 170_000)
        self.assertEqual(annual_usd("130000-170000", ""), 150_000)

    def test_drops_unusable_stored_salaries(self):
        for stored in ["€72,000", "25 - 35 USD/hour", "401k", "None", " - ", "$1,000"]:
            with self.subTest(stored=stored):
                self.assertIsNone(annual_usd(stored, ""))


class GroupingTest(unittest.TestCase):
    def test_groups_by_company(self):
        self.assertEqual(company_group("FanDuel"), "Betting & fantasy")
        self.assertEqual(company_group("Epic Games"), "Sports tech, media & gaming")
        self.assertEqual(company_group("Los Angeles Dodgers"), "Teams, leagues & orgs")
        self.assertIsNone(company_group("Headspace"))

    def test_international_is_not_an_intern(self):
        self.assertEqual(title_level("Director of International Data & Analytics"), "Senior / lead")
        self.assertEqual(title_level("Machine Learning Intern"), "Intern")
        self.assertEqual(title_level("Data Analyst"), "Mid-level")


if __name__ == "__main__":
    unittest.main()
