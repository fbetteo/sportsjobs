import markdownify
import requests

import base_scraper.companyscraper
from hetzner_utils import get_urls_by_domain, start_postgres_connection
from workable_parsing import (
    canonicalize_workable_url,
    format_locations,
    is_active_workable_job,
    title_matches_keywords,
)


COMPANIES = {
    "Rapsodo": {
        "account": "rapsodo",
        "logo": [
            {
                "url": (
                    "https://workablehr.s3.amazonaws.com/uploads/account/"
                    "open_graph_logo/602728/social"
                ),
                "filename": "rapsodo.png",
            }
        ],
    },
}


class WorkableCompanyScraper(base_scraper.companyscraper.CompanyScraper):
    REQUEST_TIMEOUT = 30

    def __init__(self, company, attributes, existing_urls, session=None):
        super().__init__(driver=None, existing_urls=existing_urls)
        self.company = company
        self.account = attributes["account"]
        self.logo = attributes["logo"]
        self.session = session or requests.Session()
        self.keywords = [*self.keywords, "ai"]
        self.existing_urls = {
            canonicalize_workable_url(url, self.account)
            for url in existing_urls
            if url
        }
        self.recent_urls = list(self.existing_urls)

    @property
    def listing_api_url(self):
        return (
            "https://apply.workable.com/api/v1/widget/accounts/"
            f"{self.account}"
        )

    def detail_api_url(self, shortcode):
        return (
            "https://apply.workable.com/api/v2/accounts/"
            f"{self.account}/jobs/{shortcode}"
        )

    def public_job_url(self, shortcode):
        return canonicalize_workable_url(
            f"https://apply.workable.com/{self.account}/j/{shortcode}",
            self.account,
        )

    def open_site(self):
        # Workable exposes listings and details through public JSON endpoints.
        return None

    def get_jobs_available(self):
        response = self.session.get(
            self.listing_api_url,
            timeout=self.REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        postings = response.json().get("jobs", [])

        jobs = []
        seen_urls = set()
        for posting in postings:
            title = (posting.get("title") or "").strip()
            shortcode = posting.get("shortcode")
            if not title or not shortcode:
                continue
            if not title_matches_keywords(title, self.keywords):
                continue

            url = self.public_job_url(shortcode)
            if url in seen_urls or url in self.existing_urls:
                continue

            seen_urls.add(url)
            jobs.append(
                {
                    "title": title,
                    "url": url,
                    "shortcode": shortcode,
                    "hours": posting.get("employment_type") or "Full-time",
                }
            )

        print(
            f"Found {len(jobs)} new matching Workable jobs "
            f"for {self.company} ({len(postings)} active listings checked)"
        )
        return jobs

    def _scrape_job(self, job):
        try:
            response = self.session.get(
                self.detail_api_url(job["shortcode"]),
                timeout=self.REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            job_info = response.json()

            if not is_active_workable_job(job_info):
                print(f"Skipping inactive Workable job: {job['title']}")
                return None

            canonical_url = self.public_job_url(job_info["shortcode"])
            if canonical_url in self.existing_urls:
                return None
            job["url"] = canonical_url

            sections = []
            for heading, field in (
                ("Description", "description"),
                ("Requirements", "requirements"),
                ("Benefits", "benefits"),
            ):
                content = job_info.get(field)
                if content:
                    sections.append(f"<h2>{heading}</h2>{content}")
            full_description = markdownify.markdownify(
                "".join(sections),
                heading_style="ATX",
            )

            locations = job_info.get("locations") or []
            location_value = format_locations(locations)
            primary_location = job_info.get("location") or {}
            country = primary_location.get("country")
            country_code = primary_location.get("countryCode")

            workplace = job_info.get("workplace")
            is_remote = job_info.get("remote", False) or workplace in {
                "remote",
                "hybrid",
            }
            if is_remote:
                work_mode = "Hybrid" if workplace == "hybrid" else "Remote"
                location_value = f"{location_value}, {work_mode}".strip(", ")

            other_data = {"company": self.company}
            if country:
                other_data["country"] = country.lower()
            if country_code:
                other_data["country_code"] = country_code.upper()
            if is_remote:
                other_data["remote"] = "Yes"
                other_data["remote_office"] = (
                    "Remote" if country else "Global Remote"
                )

            return {
                "job": job,
                "location_value": location_value,
                "hours": job["hours"],
                "full_description": full_description,
                "other_data": other_data,
            }
        except (
            requests.RequestException,
            AttributeError,
            KeyError,
            TypeError,
            ValueError,
        ) as error:
            print(f"Error fetching Workable job {job['url']}: {error}")
            return None


def get_existing_workable_urls():
    conn = start_postgres_connection()
    try:
        with conn as conn:
            return get_urls_by_domain(conn, "apply.workable.com")
    finally:
        if conn and conn.closed == 0:
            conn.close()
            print("Connection closed.")


def main():
    existing_urls = get_existing_workable_urls()
    for company, attributes in COMPANIES.items():
        print(f"Running Workable scraper for {company}")
        scraper = WorkableCompanyScraper(
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
