import unittest

from smartrecruiters_parsing import description_html, location_fields, public_job_url


class SmartRecruitersParsingTests(unittest.TestCase):
    def test_public_url_has_no_title_slug(self):
        self.assertEqual(
            public_job_url("Sportradar", "744000155753385"),
            "https://jobs.smartrecruiters.com/Sportradar/744000155753385",
        )

    def test_description_keeps_job_sections_and_skips_empty_ones(self):
        job_ad = {
            "sections": {
                "companyDescription": {"title": "Company", "text": "<p>About us</p>"},
                "jobDescription": {"title": "Job Description", "text": "<p>Build models</p>"},
                "qualifications": {"title": "Qualifications", "text": ""},
            }
        }
        self.assertEqual(
            description_html(job_ad),
            "<h2>Job Description</h2><p>Build models</p>",
        )

    def test_on_site_location(self):
        self.assertEqual(
            location_fields(
                {
                    "country": "gb",
                    "remote": False,
                    "hybrid": False,
                    "fullLocation": "London, England, United Kingdom",
                }
            ),
            {
                "location_value": "London, England, United Kingdom",
                "country": "united kingdom",
                "country_code": "GB",
            },
        )

    def test_location_without_region_has_no_empty_part(self):
        fields = location_fields({"country": "si", "fullLocation": "Ljubljana, , Slovenia"})
        self.assertEqual(fields["location_value"], "Ljubljana, Slovenia")
        self.assertEqual(fields["country"], "slovenia")

    def test_hybrid_location_is_marked_remote(self):
        fields = location_fields(
            {"country": "at", "hybrid": True, "fullLocation": "Vienna, Austria"}
        )
        self.assertEqual(fields["location_value"], "Vienna, Austria, Hybrid")
        self.assertEqual(fields["remote"], "Yes")


if __name__ == "__main__":
    unittest.main()
