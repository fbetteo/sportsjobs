import markdownify
import requests

import base_scraper.companyscraper
from hetzner_utils import get_urls_by_domain, start_postgres_connection
from job_titles import title_matches_keywords
from smartrecruiters_parsing import (
    SMARTRECRUITERS_DOMAIN,
    description_html,
    location_fields,
    public_job_url,
)


# To add a company, take the identifier from its jobs.smartrecruiters.com/<identifier> URL.
COMPANIES = {
    "Sportradar": {
        "identifier": "Sportradar",
        "logo": [
            {
                "url": "https://upload.wikimedia.org/wikipedia/commons/0/0d/Sportradar_logo.svg",
                "filename": "sportradar.svg",
            }
        ],
    },
    "Entain": {
        "identifier": "Entain",
        "logo": [
            {
                "url": "https://upload.wikimedia.org/wikipedia/commons/9/9f/Entain_Logo_2020.svg",
                "filename": "entain.svg",
            }
        ],
    },
    "Tipico": {
        "identifier": "Tipico",
        "logo": [
            {
                "url": "https://upload.wikimedia.org/wikipedia/commons/a/a6/Tipico_Logo.svg",
                "filename": "tipico.svg",
            }
        ],
    },
}

API_URL = "https://api.smartrecruiters.com/v1/companies"


class SmartRecruitersCompanyScraper(base_scraper.companyscraper.CompanyScraper):
    REQUEST_TIMEOUT = 30
    PAGE_SIZE = 100

    def __init__(self, company, attributes, existing_urls, session=None):
        super().__init__(driver=None, existing_urls=existing_urls)
        self.company = company
        self.identifier = attributes["identifier"]
        self.logo = attributes["logo"]
        self.session = session or requests.Session()
        self.keywords = [*self.keywords, "ai", "quant", "trader", "trading"]

    @property
    def postings_api_url(self):
        return f"{API_URL}/{self.identifier}/postings"

    def open_site(self):
        # SmartRecruiters exposes listings and details through public JSON endpoints.
        return None

    def get_jobs_available(self):
        postings = []
        while True:
            response = self.session.get(
                self.postings_api_url,
                params={"limit": self.PAGE_SIZE, "offset": len(postings)},
                timeout=self.REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            data = response.json()
            page = data.get("content", [])
            postings.extend(page)
            if not page or len(postings) >= data.get("totalFound", 0):
                break

        jobs = []
        for posting in postings:
            title = (posting.get("name") or "").strip()
            if not title or not title_matches_keywords(title, self.keywords):
                continue

            url = public_job_url(self.identifier, posting["id"])
            if url in self.recent_urls:
                continue

            jobs.append(
                {
                    "title": title,
                    "url": url,
                    "posting_id": posting["id"],
                }
            )

        print(
            f"Found {len(jobs)} new matching SmartRecruiters jobs "
            f"for {self.company} ({len(postings)} open listings checked)"
        )
        return jobs

    def _scrape_job(self, job):
        try:
            response = self.session.get(
                f"{self.postings_api_url}/{job['posting_id']}",
                timeout=self.REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            posting = response.json()
            if not posting.get("active", True):
                print(f"Skipping inactive SmartRecruiters job: {job['title']}")
                return None

            full_description = markdownify.markdownify(
                description_html(posting.get("jobAd", {})),
                heading_style="ATX",
            )
            location = location_fields(posting.get("location") or {})
            other_data = {"company": self.company}
            for field in ("country", "country_code", "remote"):
                if field in location:
                    other_data[field] = location[field]

            return {
                "job": job,
                "location_value": location["location_value"],
                "hours": (posting.get("typeOfEmployment") or {}).get("label")
                or "Full-time",
                "full_description": full_description,
                "other_data": other_data,
            }
        except (requests.RequestException, ValueError) as error:
            print(f"Error fetching SmartRecruiters job {job['url']}: {error}")
            return None


def get_existing_smartrecruiters_urls():
    conn = start_postgres_connection()
    try:
        with conn as conn:
            return get_urls_by_domain(conn, SMARTRECRUITERS_DOMAIN)
    finally:
        if conn and conn.closed == 0:
            conn.close()
            print("Connection closed.")


def main():
    existing_urls = get_existing_smartrecruiters_urls()
    for company, attributes in COMPANIES.items():
        print(f"Running SmartRecruiters scraper for {company}")
        scraper = SmartRecruitersCompanyScraper(
            company,
            attributes,
            existing_urls=existing_urls,
        )
        try:
            scraper.main()
        finally:
            scraper.session.close()


if __name__ == "__main__":
    main()
