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


# Replace "YourCompanyName" with the actual company name
class JobsInFootballDataScience(base_scraper.companyscraper.CompanyScraper):

    def __init__(self, driver=None, keywords=None):
        super().__init__(driver=driver, keywords=keywords)
        self.company = ""
        self.logo = [
            {
                "url": "",
                "filename": "",
            }
        ]
        self.base_url = "https://jobsinfootball.com/categories/data-science/"

    def open_site(self):
        self.driver.get(self.base_url)
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, ".media.well.listing-item.listing-item__jobs")
                )
            )
        except:
            print("Failed to load job listings")
            exit()

    def get_jobs_available(self):
        jobs_rows = []
        # find the different jobs, could be rows, divs, title, whatever is easier to loop
        # then also get the title text, which you will lower()
        jobs = [
            job
            for job in self.driver.find_elements(
                By.CSS_SELECTOR, ".media.well.listing-item.listing-item__jobs"
            )
            if any(
                keyword
                in job.find_element(
                    By.CSS_SELECTOR, ".media-heading.listing-item__title a"
                ).text.lower()
                for keyword in self.keywords
            )
        ]

        # for each job row, extract the title and the associated url
        jobs_rows = [
            {
                "title": job.find_element(
                    By.CSS_SELECTOR, ".media-heading.listing-item__title a"
                ).text,
                "url": job.find_element(
                    By.CSS_SELECTOR, ".media-heading.listing-item__title a"
                ).get_attribute("href"),
            }
            for job in jobs
        ]
        return jobs_rows

    def _scrape_job(self, job):
        try:
            self.driver.get(job["url"])
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".details-header"))
            )

            self.company = self.driver.find_element(
                By.CSS_SELECTOR,
                ".listing-item__info--item-company",
            ).text

            # Get the logo
            image_element = self.driver.find_element(
                By.CSS_SELECTOR, ".sidebar__content .profile__image img"
            )
            self.logo[0]["url"] = image_element.get_attribute("src")
            self.logo[0]["filename"] = f"{self.company}.png"

            # Extract location
            location_element = self.driver.find_element(
                By.CSS_SELECTOR,
                ".listing-item__info--item-location",
            )
            location_value = location_element.text
            hours = "Full-time"
            # replace with all the job description html
            description_raw = self.driver.find_element(
                By.CSS_SELECTOR, ".details-body__content.content-text"
            ).get_attribute("innerHTML")

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


class JobsInFootballDataAnalyst(base_scraper.companyscraper.CompanyScraper):

    def __init__(self, driver=None, keywords=None):
        super().__init__(driver=driver, keywords=keywords)
        self.company = ""
        self.logo = [
            {
                "url": "",
                "filename": "",
            }
        ]
        self.base_url = (
            "https://jobsinfootball.com/jobs/?q=data%20analyst&job_type[]=Full%20time"
        )

    def open_site(self):
        self.driver.get(self.base_url)
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, ".media.well.listing-item.listing-item__jobs")
                )
            )
        except:
            print("Failed to load job listings")
            exit()

    def get_jobs_available(self):
        jobs_rows = []
        # find the different jobs, could be rows, divs, title, whatever is easier to loop
        # then also get the title text, which you will lower()
        jobs = [
            job
            for job in self.driver.find_elements(
                By.CSS_SELECTOR, ".media.well.listing-item.listing-item__jobs"
            )
            if any(
                keyword
                in job.find_element(
                    By.CSS_SELECTOR, ".media-heading.listing-item__title a"
                ).text.lower()
                for keyword in self.keywords
            )
        ]

        # for each job row, extract the title and the associated url
        jobs_rows = [
            {
                "title": job.find_element(
                    By.CSS_SELECTOR, ".media-heading.listing-item__title a"
                ).text,
                "url": job.find_element(
                    By.CSS_SELECTOR, ".media-heading.listing-item__title a"
                ).get_attribute("href"),
            }
            for job in jobs
        ]
        return jobs_rows

    def _scrape_job(self, job):
        try:
            self.driver.get(job["url"])
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".details-header"))
            )

            self.company = self.driver.find_element(
                By.CSS_SELECTOR,
                ".listing-item__info--item-company",
            ).text

            # Get the logo
            image_element = self.driver.find_element(
                By.CSS_SELECTOR, ".sidebar__content .profile__image img"
            )
            self.logo[0]["url"] = image_element.get_attribute("src")
            self.logo[0]["filename"] = f"{self.company}.png"

            # Extract location
            location_element = self.driver.find_element(
                By.CSS_SELECTOR,
                ".listing-item__info--item-location",
            )
            location_value = location_element.text
            hours = "Full-time"
            # replace with all the job description html
            description_raw = self.driver.find_element(
                By.CSS_SELECTOR, ".details-body__content.content-text"
            ).get_attribute("innerHTML")

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


teams = [
    JobsInFootballDataScience,
    JobsInFootballDataAnalyst,
]

for team in teams:
    # try:
    print(f"Running {team.__name__} main()")
    team_instance = team(driver=driver)
    team_instance.main()
driver.quit()
