import unittest

from adp_parsing import (
    external_job_id,
    format_locations,
    minimum_salary,
    public_job_url,
)

# Trimmed from a real Boston Celtics requisition (October 2026).
REQUISITION = {
    "itemID": "9201269364652_1",
    "requisitionTitle": "Application & AI Integration Engineer",
    "payGradeRange": {
        "minimumRate": {"amountValue": 95000.0, "currencyCode": "USD"},
        "maximumRate": {"amountValue": 125000.0, "currencyCode": "USD"},
    },
    "customFieldGroup": {
        "stringFields": [
            {"nameCode": {"codeValue": "CareerCenterRefId"}},
            {"stringValue": "591452", "nameCode": {"codeValue": "ExternalJobID"}},
        ]
    },
    "requisitionLocations": [
        {"nameCode": {"shortName": " Boston, MA, US"}},
        {"nameCode": {"shortName": "Boston, MA, US"}},
    ],
}


class ADPParsingTests(unittest.TestCase):
    def test_public_url_uses_external_job_id(self):
        self.assertEqual(
            public_job_url("abc-cid", "123_2", external_job_id(REQUISITION)),
            "https://workforcenow.adp.com/mascsr/default/mdf/recruitment/"
            "recruitment.html?cid=abc-cid&ccId=123_2&jobId=591452"
            "&lang=en_US&selectedMenuKey=CurrentOpenings",
        )

    def test_missing_external_job_id(self):
        self.assertIsNone(external_job_id({"customFieldGroup": {}}))

    def test_formats_locations_without_duplicates(self):
        self.assertEqual(format_locations(REQUISITION), "Boston, MA, US")

    def test_minimum_salary(self):
        self.assertEqual(minimum_salary(REQUISITION), "$95,000")
        self.assertIsNone(minimum_salary({}))


if __name__ == "__main__":
    unittest.main()
