import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import base_scraper.companyscraper
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
import re
import utils
import markdownify


class Liverpool(base_scraper.companyscraper.CompanyScraper):

    def __init__(self, driver=None, keywords=None):
        super().__init__(driver=driver, keywords=keywords)
        self.company = "Liverpool FC"
        self.logo = [
            {
                "url": "https://upload.wikimedia.org/wikipedia/en/thumb/0/0c/Liverpool_FC.svg/180px-Liverpool_FC.svg.png",
                "filename": "liverpoolfc.png",
            }
        ]
        self.base_url = "https://jobsearch.liverpoolfc.com/"

    def open_site(self):
        self.driver.get(self.base_url)
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "results"))
            )
        except:
            print("Failed to load job listings")
            exit()

    def get_jobs_available(self):
        jobs_rows = []
        jobs = [
            job
            for job in self.driver.find_elements(By.CSS_SELECTOR, "#results .jobs li a")
            if any(
                keyword
                in job.find_element(By.CSS_SELECTOR, ".job-list-title").text.lower()
                for keyword in self.keywords
            )
        ]

        jobs_rows = [
            {
                "title": job.find_element(By.CSS_SELECTOR, ".job-list-title").text,
                "url": job.get_attribute("href"),
            }
            for job in jobs
        ]
        return jobs_rows

    def _scrape_job(self, job):
        try:
            self.driver.get(job["url"])
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "job_main"))
            )

            location_value = "Kirkby, United Kingdom"
            hours = "Full-time"

            description_raw = self.driver.find_element(
                By.CSS_SELECTOR, ".feature-text"
            ).get_attribute("innerHTML")
            # soup = BeautifulSoup(description_raw, "html.parser")
            # description = soup.get_text(separator="\n").strip()
            # full_description = f"{description}"
            full_description = markdownify.markdownify(
                description_raw, heading_style="ATX"
            )

            return {
                "job": job,
                "location_value": location_value,
                "hours": hours,
                "full_description": full_description,
            }
        except Exception as e:
            print(f"Error extracting event: {e}")
            return None


chrome_options = Options()
# required with the current docker image
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--remote-debugging-port=9222")
chrome_options.add_argument("--disable-gpu")

driver = webdriver.Chrome(options=chrome_options)
teams = [Liverpool]

for team in teams:
    # try:
    print(f"Running {team.__name__} main()")
    team_instance = team(driver=driver)
    team_instance.main()
# except Exception as e:
#     print(f"Error running {team.__name__} main(): {e}")
driver.quit()
