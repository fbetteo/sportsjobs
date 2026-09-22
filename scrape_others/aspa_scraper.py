import os
import sys
from datetime import date

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import markdownify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import base_scraper.companyscraper
from scrape_others.aspa_parsing import (
    canonicalize_job_url,
    extract_location,
    has_closed,
    is_recent_post,
    split_title_and_company,
)


class ASPAScraper(base_scraper.companyscraper.CompanyScraper):
    RECENT_DAYS = 7
    CATEGORY_URLS = [
        "https://theaspa.org/jobs-board?blogcategory=Data+Scientist",
        "https://theaspa.org/jobs-board?blogcategory=Data+Engineer",
        "https://theaspa.org/jobs-board?blogcategory=Data+Analyst",
        "https://theaspa.org/jobs-board?blogcategory=Research+%2F+PhD",
    ]
    CARD_SELECTOR = '[data-aid^="RSS_FEED_RENDERED_"]'

    def __init__(self, driver=None, keywords=None):
        super().__init__(driver=driver, keywords=keywords)
        self.company = "TheASPA"
        self.base_url = self.CATEGORY_URLS[0]
        self.recent_urls_canonical = {
            canonicalize_job_url(url) for url in self.recent_urls if url
        }

    def _open_listing(self, url):
        self.driver.get(url)
        WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, self.CARD_SELECTOR))
        )

    def open_site(self):
        self._open_listing(self.base_url)

    def _get_current_page_jobs(self):
        jobs = []
        today = date.today()

        for card in self.driver.find_elements(By.CSS_SELECTOR, self.CARD_SELECTOR):
            try:
                source_title = card.find_element(By.TAG_NAME, "h4").text.strip()
                published_date = card.find_element(
                    By.CSS_SELECTOR, '[data-aid="RSS_FEED_POST_DATE_RENDERED"]'
                ).text.strip()
                summary = card.find_element(
                    By.CSS_SELECTOR, '[data-aid="RSS_FEED_POST_CONTENT_RENDERED"]'
                ).text.strip()
                url = canonicalize_job_url(
                    card.find_element(By.XPATH, "./ancestor::a[1]").get_attribute(
                        "href"
                    )
                )
            except Exception as error:
                print(f"Skipping malformed ASPA listing card: {error}")
                continue

            if not is_recent_post(
                published_date,
                today=today,
                max_age_days=self.RECENT_DAYS,
            ):
                continue
            if has_closed(summary, today=today):
                print(f"Skipping closed ASPA job: {source_title}")
                continue
            if url in self.recent_urls_canonical:
                print(f"ASPA job already exists in the database: {source_title}")
                continue

            title, company = split_title_and_company(source_title)
            jobs.append(
                {
                    "title": title,
                    "url": url,
                    "company": company,
                    "summary": summary,
                }
            )

        return jobs

    def get_jobs_available(self):
        jobs_by_url = {}

        for index, category_url in enumerate(self.CATEGORY_URLS):
            if index > 0:
                self._open_listing(category_url)
            for job in self._get_current_page_jobs():
                jobs_by_url.setdefault(job["url"], job)

        print(f"Found {len(jobs_by_url)} recent, unique ASPA jobs")
        return list(jobs_by_url.values())

    def _scrape_job(self, job):
        try:
            self.driver.get(job["url"])
            content = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, '[data-ux="BlogContent"]')
                )
            )

            self.company = job["company"]
            try:
                logo_url = self.driver.find_element(
                    By.CSS_SELECTOR, 'meta[property="og:image"]'
                ).get_attribute("content")
            except Exception:
                logo_url = ""
            self.logo = [
                {
                    "url": logo_url,
                    "filename": f"{self.company}.png",
                }
            ]

            description_html = content.get_attribute("innerHTML")
            full_description = markdownify.markdownify(
                description_html,
                heading_style="ATX",
            )
            if has_closed(content.text, today=date.today()):
                print(f"Skipping closed ASPA job: {job['title']}")
                return None

            location_value = extract_location(job["summary"])
            if not location_value:
                location_value = extract_location(content.text)

            summary_lower = job["summary"].lower()
            hours = (
                "Part-time"
                if "part-time" in summary_lower or "part time" in summary_lower
                else "Full-time"
            )

            return {
                "job": job,
                "location_value": location_value,
                "hours": hours,
                "full_description": full_description,
                "other_data": {"company": self.company},
            }
        except Exception as error:
            print(f"Error extracting ASPA job {job['url']}: {error}")
            return None


def main():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=chrome_options)
    try:
        ASPAScraper(driver=driver).main()
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
