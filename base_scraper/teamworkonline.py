import os
import time
from urllib.parse import urljoin

import markdownify
import requests
from bs4 import BeautifulSoup

from base_scraper.companyscraper import BROWSER_USER_AGENT, CompanyScraper

# TeamWork Online's Cloudflare check challenges headless Chrome but serves plain
# HTTP requests, so these pages are fetched with requests instead of Selenium.
session = requests.Session()
session.headers.update(
    {
        "User-Agent": BROWSER_USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
)

# Cloudflare also blocks datacenter IPs (e.g. the Hetzner server), so production
# routes these requests through a rotating residential proxy, such as Webshare's
# http://USERNAME:PASSWORD@p.webshare.io:80. Unset means a direct connection.
PROXY_URL = os.getenv("TEAMWORK_PROXY_URL")
if PROXY_URL:
    session.proxies.update({"http": PROXY_URL, "https": PROXY_URL})

SECONDS_BETWEEN_REQUESTS = 1
# A rotating proxy uses a new IP per request, so a blocked request is worth retrying.
ATTEMPTS_PER_PAGE = 3


def clean_text(element):
    return " ".join(element.get_text(" ").split())


class TeamworkOnlineScraper(CompanyScraper):
    """A TeamWork Online job board.

    League boards list jobs from many teams: set company_from_job_page so each
    job takes the team name and logo from its own page. Single-team boards keep
    the company and logo set in __init__.
    """

    company_from_job_page = False
    sport_list = None  # e.g. ["Baseball"], passed on as other_data
    title_suffix = ""  # e.g. " - NHL", helps utils.add_sport_list() find the sport

    def fetch(self, url):
        for attempt in range(1, ATTEMPTS_PER_PAGE + 1):
            time.sleep(SECONDS_BETWEEN_REQUESTS)
            response = session.get(url, timeout=30)
            if response.status_code != 403 or attempt == ATTEMPTS_PER_PAGE:
                break
            print(f"403 from TeamWork Online, retrying ({attempt}/{ATTEMPTS_PER_PAGE}): {url}")
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")

    def open_site(self):
        self.listing_page = self.fetch(self.base_url)
        if not self.listing_page.select(".organization-portal__job-details"):
            print("Failed to load job listings")
            raise Exception("Failed to load TeamworkOnline job listings")

    def get_jobs_available(self):
        jobs_rows = []
        for link in self.listing_page.select(".organization-portal__job-title a"):
            title = clean_text(link)
            if any(keyword in title.lower() for keyword in self.keywords):
                jobs_rows.append(
                    {"title": title, "url": urljoin(self.base_url, link["href"])}
                )
        return jobs_rows

    def _scrape_job(self, job):
        try:
            page = self.fetch(job["url"])

            if self.company_from_job_page:
                self.company = clean_text(
                    page.select_one("div.lic-header__name > h1")
                )
                logo = page.select_one(
                    "div.lic-header__logo-wrap a.lic-header__logo-wrap--link > img"
                )
                self.logo[0]["url"] = logo["src"]
                self.logo[0]["filename"] = f"{self.company}.png"

            info_items = page.select(".opportunity-preview__info-content-item")
            hours = clean_text(info_items[0])
            location_value = clean_text(info_items[1])

            description_raw = page.select_one(
                ".opportunity-preview__body"
            ).decode_contents()
            full_description = markdownify.markdownify(
                description_raw, heading_style="ATX"
            )

            job["title"] += self.title_suffix

            job_data = {
                "job": job,
                "location_value": location_value,
                "hours": hours,
                "full_description": full_description,
            }
            if self.sport_list:
                job_data["other_data"] = {"sport_list": self.sport_list}
            return job_data
        except Exception as e:
            print(f"Error extracting event: {e}")
            return None
