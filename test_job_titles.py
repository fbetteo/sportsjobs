import unittest

from job_titles import TECH_TITLE_KEYWORDS, title_matches_keywords


class TechTitleFilterTests(unittest.TestCase):
    def test_keeps_analytics_and_engineering_titles(self):
        for title in [
            "Senior Quantitative Sports Modeler",
            "Statistician Network Coordinator",
            "Senior Trader, SeatGeek IQ",
            "Head of Sport Science",
            "Engineering Manager, Fan Experience",
            "Lead Programmer",
            "Senior Manager, ML Health - Insights",
            "Senior Data & AI Engineer",
        ]:
            with self.subTest(title=title):
                self.assertTrue(title_matches_keywords(title, TECH_TITLE_KEYWORDS))

    def test_drops_business_titles(self):
        for title in [
            "Sr. Accountant",
            "Legal Director, Privacy",
            "Junior Copywriter",
            "Director, Technical Recruiting",
            "Principal Product Manager, Basketball Products",
            "Retail Manager",
        ]:
            with self.subTest(title=title):
                self.assertFalse(title_matches_keywords(title, TECH_TITLE_KEYWORDS))

    def test_keywords_match_whole_words_only(self):
        self.assertFalse(title_matches_keywords("Paid Media Manager", ["ai"]))
        self.assertFalse(title_matches_keywords("International Sales", ["intern"]))


if __name__ == "__main__":
    unittest.main()
