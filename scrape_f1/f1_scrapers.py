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


class Mclaren(base_scraper.companyscraper.CompanyScraper):

    def __init__(self, driver=None, keywords=None):
        super().__init__(driver=driver, keywords=keywords)
        self.company = "McLaren Racing"
        self.logo = [
            {
                "url": "https://careers.recruiteecdn.com/image/upload/q_auto,f_auto,w_400,c_limit/production/images/2fU/wXL-SAbb3793.png",
                "filename": "McLaren.png",
            }
        ]
        self.base_url = "https://racingcareers.mclaren.com/"

    def open_site(self):
        self.driver.get(self.base_url)
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "table.sc-18rtkup-0 tbody tr")
                )
            )
        except:
            print("Failed to load job listings")
            exit()

    def get_jobs_available(self):
        jobs_rows = []
        jobs = [
            job
            for job in self.driver.find_elements(
                By.CSS_SELECTOR, "table.sc-18rtkup-0 tbody tr"
            )
            if any(
                keyword
                in job.find_element(By.CSS_SELECTOR, "td a.sc-18rtkup-2").text.lower()
                for keyword in self.keywords
            )
        ]

        jobs_rows = [
            {
                "title": job.find_element(By.CSS_SELECTOR, "td a.sc-18rtkup-2").text,
                "url": job.find_element(
                    By.CSS_SELECTOR, "td a.sc-18rtkup-2"
                ).get_attribute("href"),
            }
            for job in jobs
        ]
        return jobs_rows

    def _scrape_job(self, job):
        try:
            # Extract job details
            self.driver.get(job["url"])
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, ".sc-qfruxy-5 .custom-css-style-job-location")
                )
            )

            info_elements = self.driver.find_elements(
                By.CLASS_NAME, "opportunity-preview__info-content-item"
            )
            location_value = self.driver.find_element(
                By.CSS_SELECTOR, ".sc-qfruxy-5 .custom-css-style-job-location"
            ).text
            hours = "Full-time"

            description_raw = ""
            for job_section in driver.find_elements(
                By.CSS_SELECTOR, ".sc-1fwbcuw-0.lfJPrZ"
            ):
                description_raw += job_section.get_attribute("innerHTML")

            soup = BeautifulSoup(description_raw, "html.parser")
            description = soup.get_text(separator="\n").strip()
            full_description = f"{description}"

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
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--remote-debugging-port=9222")

driver = webdriver.Chrome(options=chrome_options)
teams = [Mclaren]

for team in teams:
    # try:
    print(f"Running {team.__name__} main()")
    team_instance = team(driver=driver)
    team_instance.main()


# # For debug
# driver = webdriver.Chrome()
# aa = Mclaren(driver=driver)

# aa.open_site()
# jobs = aa.get_jobs_available()

# for job in jobs[0:1]:
#     job_data = aa._scrape_job(job)
