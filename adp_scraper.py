import markdownify
import requests

import base_scraper.companyscraper
from adp_parsing import (
    ADP_DOMAIN,
    external_job_id,
    format_locations,
    minimum_salary,
    public_job_url,
)
from job_titles import title_matches_keywords
from hetzner_utils import get_urls_by_domain, start_postgres_connection


# To add a company, open its ADP "Current Openings" page and copy the
# cid and ccId query parameters from the URL.
COMPANIES = {
    "Boston Celtics": {
        "cid": "60aee0ad-011f-4b26-8df9-73f60a0520a2",
        "cc_id": "9201173610523_2",
        "logo": [
            {
                "url": "https://upload.wikimedia.org/wikipedia/en/8/8f/Boston_Celtics.svg",
                "filename": "bostonceltics.png",
            }
        ],
    },
}

API_URL = (
    f"https://{ADP_DOMAIN}/mascsr/default/careercenter/public/events/"
    "staffing/v1/job-requisitions"
)


class ADPCompanyScraper(base_scraper.companyscraper.CompanyScraper):
    REQUEST_TIMEOUT = 30
    PAGE_SIZE = 20

    def __init__(self, company, attributes, existing_urls, session=None):
        super().__init__(driver=None, existing_urls=existing_urls)
        self.company = company
        self.cid = attributes["cid"]
        self.cc_id = attributes["cc_id"]
        self.logo = attributes["logo"]
        self.session = session or requests.Session()
        self.session.headers["User-Agent"] = (
            base_scraper.companyscraper.BROWSER_USER_AGENT
        )
        self.keywords = [*self.keywords, "ai", "devops"]

    @property
    def api_params(self):
        return {
            "cid": self.cid,
            "ccId": self.cc_id,
            "lang": "en_US",
            "locale": "en_US",
        }

    def open_site(self):
        # ADP exposes listings and details through public JSON endpoints.
        return None

    def get_jobs_available(self):
        requisitions = []
        while True:
            response = self.session.get(
                API_URL,
                params={
                    **self.api_params,
                    "$top": self.PAGE_SIZE,
                    "$skip": len(requisitions),
                },
                timeout=self.REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            data = response.json()
            page = data.get("jobRequisitions", [])
            requisitions.extend(page)
            total = data.get("meta", {}).get("totalNumber", 0)
            if not page or len(requisitions) >= total:
                break

        jobs = []
        for requisition in requisitions:
            title = (requisition.get("requisitionTitle") or "").strip()
            job_id = external_job_id(requisition)
            if not title or not job_id:
                continue
            if not title_matches_keywords(title, self.keywords):
                continue

            url = public_job_url(self.cid, self.cc_id, job_id)
            if url in self.recent_urls:
                continue

            jobs.append(
                {
                    "title": title,
                    "url": url,
                    "item_id": requisition["itemID"],
                }
            )

        print(
            f"Found {len(jobs)} new matching ADP jobs "
            f"for {self.company} ({len(requisitions)} open listings checked)"
        )
        return jobs

    def _scrape_job(self, job):
        try:
            response = self.session.get(
                f"{API_URL}/{job['item_id']}",
                params=self.api_params,
                timeout=self.REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            requisition = response.json()

            full_description = markdownify.markdownify(
                requisition.get("requisitionDescription") or "",
                heading_style="ATX",
            )

            other_data = {"company": self.company}
            salary = minimum_salary(requisition)
            if salary:
                other_data["salary"] = salary

            return {
                "job": job,
                "location_value": format_locations(requisition),
                "hours": requisition.get("workLevelCode", {}).get("shortName")
                or "Full Time",
                "full_description": full_description,
                "other_data": other_data,
            }
        except (requests.RequestException, ValueError) as error:
            print(f"Error fetching ADP job {job['url']}: {error}")
            return None


def get_existing_adp_urls():
    conn = start_postgres_connection()
    try:
        with conn as conn:
            return get_urls_by_domain(conn, ADP_DOMAIN)
    finally:
        if conn and conn.closed == 0:
            conn.close()
            print("Connection closed.")


def main():
    existing_urls = get_existing_adp_urls()
    for company, attributes in COMPANIES.items():
        print(f"Running ADP scraper for {company}")
        scraper = ADPCompanyScraper(
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
