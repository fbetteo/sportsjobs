import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import base_scraper.companyscraper
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time
from bs4 import BeautifulSoup
import re
import utils
import markdownify


import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import markdownify


class SIG(base_scraper.companyscraper.CompanyScraper):

    def __init__(self, driver=None, keywords=None):
        super().__init__(driver=driver, keywords=keywords)
        self.company = "SIG"
        self.logo = [
            {
                "url": "https://sig.com/media/u5da23wc/white_susquehanna.svg",
                "filename": "sig.svg",
            }
        ]
        # your Sports Analytics category URL
        self.base_url = "https://careers.sig.com/c/sports-analytics-jobs"

    def open_site(self):
        self.driver.get(self.base_url)
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//a[contains(@href, '/job/')]")
                )
            )
        except Exception:
            print("Failed to load job listings")
            exit()

    def get_jobs_available(self):
        all_job_links = self.driver.find_elements(
            By.XPATH, "//a[contains(@href, '/job/')]"
        )
        filtered = [
            link
            for link in all_job_links
            if any(kw in link.text.lower() for kw in self.keywords)
        ]
        return [
            {"title": job.text.strip(), "url": job.get_attribute("href")}
            for job in filtered
        ]

    def _scrape_job(self, job):
        try:
            self.driver.get(job["url"])

            location_value = ""

            # 1) Wait for the JSON-LD to appear
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//script[@type='application/ld+json']")
                )
            )
            raw_json = self.driver.find_element(
                By.XPATH, "//script[@type='application/ld+json']"
            ).get_attribute("innerHTML")
            data = json.loads(raw_json)

            # 3) Employment type → hours
            #    e.g. "Full-time", "Part-time"
            hours = "Full-time"

            # 4) Description HTML → Markdown
            desc_html = data.get("description", "")
            full_description = markdownify.markdownify(desc_html, heading_style="ATX")

            # 5) (Optional) tag title if you like
            # job["title"] += " - Sports Analytics @ SIG"

            return {
                "job": job,
                "location_value": location_value,
                "hours": hours,
                "full_description": full_description,
            }

        except Exception as e:
            print(f"Error extracting job details for {job['url']}: {e}")
            # fallback: try scraping via CSS/XPath directly
            try:
                # wait for the detail section to load
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.TAG_NAME, "article"))
                )
                # fallback location
                loc_el = self.driver.find_element(
                    By.XPATH,
                    "//li[contains(translate(., 'LOCATION','location'),'location')]/span",
                )
                location_value = loc_el.text.strip()
                # fallback description
                raw = self.driver.find_element(By.TAG_NAME, "article").get_attribute(
                    "innerHTML"
                )
                full_description = markdownify.markdownify(raw, heading_style="ATX")
                return {
                    "job": job,
                    "location_value": location_value,
                    "hours": "Full-time",
                    "full_description": full_description,
                }
            except Exception as ee:
                print(f"Fallback also failed: {ee}")
                return None


class Disney(base_scraper.companyscraper.CompanyScraper):

    def __init__(self, driver=None, keywords=None):
        super().__init__(driver=driver, keywords=keywords)
        self.company = "Disney"
        self.logo = [
            {
                "url": "https://upload.wikimedia.org/wikipedia/commons/3/3e/Disney_wordmark.svg",
                "filename": "disney.svg",
            }
        ]
        # Data Science & Analytics category page
        self.base_url = (
            "https://jobs.disneycareers.com/category/"
            "data-science-and-analytics-jobs/391-28648/8221776/1"
        )

    def open_site(self):
        # 1) Go to the DS&A page
        self.driver.get(self.base_url)

        # 2) Wait for the Business facet toggle to appear
        toggle = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(
                (By.ID, "custom_fields.industrycustomfield-toggle")
            )
        )

        # 3) Expand Business if collapsed
        if toggle.get_attribute("aria-expanded") == "false":
            toggle.click()

        # 4) Wait for the ESPN filter option under Business to appear
        espn_label = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//label[@for='custom_fields.industrycustomfield-filter-6']")
            )
        )  # ESPN is listed under Business :contentReference[oaicite:0]{index=0}

        # 5) Click ESPN and wait for listings to refresh
        #    (use staleness_of to detect the Ajax‐driven reload)
        first_job = self.driver.find_element(By.XPATH, "//a[contains(@href, '/job/')]")
        espn_label.click()
        WebDriverWait(self.driver, 10).until(EC.staleness_of(first_job))
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/job/')]"))
        )

    def get_jobs_available(self):
        links = self.driver.find_elements(By.XPATH, "//a[contains(@href, '/job/')]")
        return [
            {"title": link.text.strip(), "url": link.get_attribute("href")}
            for link in links
        ]

    def _scrape_job(self, job):
        try:
            self.driver.get(job["url"])
            # 1) Wait for the title <h1>
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "h1"))
            )

            # 2) Pull the meta block (the container right after <h1>) :contentReference[oaicite:0]{index=0}
            meta_elem = self.driver.find_element(
                By.XPATH, "//h1/following-sibling::*[1]"
            )
            meta_text = meta_elem.text
            # Extract location via regex
            m = re.search(r"Location\s+(.+?)(?:\s{2,}|$)", meta_text)
            location_value = m.group(1).strip() if m else ""
            hours = "Full Time"  # all roles here are full-time

            # 3) Collect everything *after* that meta block until “About Disney”
            desc_raw = ""
            siblings = meta_elem.find_elements(By.XPATH, "following-sibling::*")
            for elem in siblings:
                txt = elem.text.strip()
                # stop when we hit the About Disney Experiences section :contentReference[oaicite:1]{index=1}
                if txt.startswith("About Disney") or txt.startswith(
                    "About The Walt Disney Company"
                ):
                    break
                # skip any Apply-buttons container
                if (
                    "Apply Now" in txt
                    or "Apply Later" in txt
                    or "Current Employees Apply" in txt
                ):
                    continue
                # otherwise include its full HTML
                desc_raw += elem.get_attribute("outerHTML")

            # 4) Convert the full blob to Markdown
            full_description = markdownify.markdownify(desc_raw, heading_style="ATX")

            return {
                "job": job,
                "location_value": location_value,
                "hours": hours,
                "full_description": full_description,
            }

        except Exception as e:
            print(f"Error extracting job details for {job['url']}: {e}")
            return None


chrome_options = Options()
# required with the current docker image
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--remote-debugging-port=9222")
chrome_options.add_argument("--disable-gpu")

driver = webdriver.Chrome(options=chrome_options)

# Disney not working, I need to filter by Espn (I'm tired)
for team in [SIG]:
    print(f"Running {team.__name__} main()")
    team_instance = team(driver=driver)
    team_instance.main()

# driver = webdriver.Chrome(options=chrome_options)

# driver.get("https://careers.sig.com/c/sports-analytics-jobs")

# try:
#     # wait for at least one job link to appear
#     WebDriverWait(driver, 10).until(
#         EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/job/')]"))
#     )
# except Exception:
#     print("Failed to load job listings")
#     exit()

# all_job_links = driver.find_elements(By.XPATH, "//a[contains(@href, '/job/')]")

# all_job_links
# # filter by keyword
# jobs = [
#     link
#     for link in all_job_links
#     if any(kw in link.text.lower() for kw in self.keywords)
# ]
# # build list of {"title", "url"}
# jobs_rows = [
#     {
#         "title": job.text.strip(),
#         "url": job.get_attribute("href"),
#     }
#     for job in jobs
# ]
# # aa = VancouverCanucks(driver=driver)

# aa = Disney(driver=driver)

# aa.open_site()
# jobs = aa.get_jobs_available()
# jobs
# for job in jobs[0:1]:
#     job_data = aa._scrape_job(job)

# job_data
