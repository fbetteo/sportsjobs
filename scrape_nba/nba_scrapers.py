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


class DetroitPistons(base_scraper.companyscraper.CompanyScraper):

    def __init__(self, driver=None, keywords=None):
        super().__init__(driver=driver, keywords=keywords)
        self.company = "Detroit Pistons"
        self.logo = [
            {
                "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/Logo_of_the_Detroit_Pistons.svg/150px-Logo_of_the_Detroit_Pistons.svg.png",
                "filename": "detroitpistons.png",
            }
        ]
        self.base_url = "https://www.teamworkonline.com/basketball-jobs/palacenet/detroit-pistons-jobs-"

    def open_site(self):
        self.driver.get(self.base_url)
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, "organization-portal__job-details")
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
                By.CLASS_NAME, "organization-portal__job-title"
            )
            if any(keyword in job.text.lower() for keyword in self.keywords)
        ]

        jobs_rows = [
            {
                "title": job.find_element(By.TAG_NAME, "a").text,
                "url": job.find_element(By.TAG_NAME, "a").get_attribute("href"),
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
                    (By.CLASS_NAME, "opportunity-preview__body")
                )
            )

            info_elements = self.driver.find_elements(
                By.CLASS_NAME, "opportunity-preview__info-content-item"
            )
            location_value = info_elements[1].text
            hours = info_elements[0].text

            description_raw = self.driver.find_element(
                By.CLASS_NAME, "opportunity-preview__body"
            ).get_attribute("innerHTML")
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


class GoldenStateWarriors(base_scraper.companyscraper.CompanyScraper):

    def __init__(self, driver=None, keywords=None):
        super().__init__(driver=driver, keywords=keywords)
        self.company = "Golden Stante Warriors"
        self.logo = [
            {
                "url": "https://upload.wikimedia.org/wikipedia/en/thumb/0/01/Golden_State_Warriors_logo.svg/200px-Golden_State_Warriors_logo.svg.png",
                "filename": "goldenstatewarriors.png",
            }
        ]
        self.base_url = "https://www.teamworkonline.com/basketball-jobs/warriors/golden-state-warriors-careers"

    def open_site(self):
        self.driver.get(self.base_url)
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, "organization-portal__job-details")
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
                By.CLASS_NAME, "organization-portal__job-title"
            )
            if any(keyword in job.text.lower() for keyword in self.keywords)
        ]

        jobs_rows = [
            {
                "title": job.find_element(By.TAG_NAME, "a").text,
                "url": job.find_element(By.TAG_NAME, "a").get_attribute("href"),
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
                    (By.CLASS_NAME, "opportunity-preview__body")
                )
            )

            info_elements = self.driver.find_elements(
                By.CLASS_NAME, "opportunity-preview__info-content-item"
            )
            location_value = info_elements[1].text
            hours = info_elements[0].text
            team = info_elements[0].text.split(" - ")[0]
            other_data = {"company": team}

            description_raw = self.driver.find_element(
                By.CLASS_NAME, "opportunity-preview__body"
            ).get_attribute("innerHTML")
            soup = BeautifulSoup(description_raw, "html.parser")
            description = soup.get_text(separator="\n").strip()
            full_description = f"{description}"

            return {
                "job": job,
                "location_value": location_value,
                "hours": hours,
                "full_description": full_description,
                "other_data": other_data,
            }
        except Exception as e:
            print(f"Error extracting event: {e}")
            return None


class HoustonRockets(base_scraper.companyscraper.CompanyScraper):

    def __init__(self, driver=None, keywords=None):
        super().__init__(driver=driver, keywords=keywords)
        self.company = "Houston Rockets"
        self.logo = [
            {
                "url": "https://upload.wikimedia.org/wikipedia/en/thumb/2/28/Houston_Rockets.svg/170px-Houston_Rockets.svg.png",
                "filename": "houstonrockets.png",
            }
        ]
        self.base_url = "https://recruitingbypaycor.com/career/CareerHome.action?clientId=8a7883c689b7fbd50189ffa65b61208d"

    def open_site(self):
        self.driver.get(self.base_url)
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, "gnewtonCareerGroupJobTitleClass")
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
                By.CLASS_NAME, "gnewtonCareerGroupJobTitleClass"
            )
            if any(keyword in job.text.lower() for keyword in self.keywords)
        ]

        jobs_rows = [
            {
                "title": job.find_element(By.TAG_NAME, "a").text,
                "url": job.find_element(By.TAG_NAME, "a").get_attribute("href"),
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
                    (By.CLASS_NAME, "gnewtonCareerBodyClass")
                )
            )

            location_value = "Houston, TX"
            hours = "Full-time"

            description_raw = self.driver.find_element(
                By.ID, "gnewtonJobDescriptionText"
            ).text
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


class IndianaPacers(base_scraper.companyscraper.CompanyScraper):

    def __init__(self, driver=None, keywords=None):
        super().__init__(driver=driver, keywords=keywords)
        self.company = "Indiana Pacers"
        self.logo = [
            {
                "url": "https://upload.wikimedia.org/wikipedia/en/thumb/1/1b/Indiana_Pacers.svg/200px-Indiana_Pacers.svg.png",
                "filename": "indianapacers.png",
            }
        ]
        self.base_url = (
            "https://pse.hrmdirect.com/employment/job-openings.php?search=true&"
        )

    def open_site(self):
        self.driver.get(self.base_url)
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "reqResultTable"))
            )
        except:
            print("Failed to load job listings")
            exit()

    def get_jobs_available(self):
        job_table = driver.find_element(By.CLASS_NAME, "reqResultTable")
        jobs_rows = []
        # slicing to remove the header row
        jobs = [
            job
            for job in job_table.find_elements(By.TAG_NAME, "tr")[1:]
            if any(
                keyword
                in job.find_element(By.CSS_SELECTOR, "td.posTitle a").text.lower()
                for keyword in self.keywords
            )
        ]

        jobs_rows = [
            {
                "title": job.find_element(By.CSS_SELECTOR, "td.posTitle a").text,
                "url": job.find_element(By.CSS_SELECTOR, "td.posTitle a").get_attribute(
                    "href"
                ),
            }
            for job in jobs
        ]
        return jobs_rows

    def _scrape_job(self, job):
        try:
            # Extract job details
            self.driver.get(job["url"])
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.jobDesc"))
            )

            info_elements = self.driver.find_element(By.CLASS_NAME, "viewFields")

            location_value = info_elements.find_elements(
                By.CLASS_NAME, "viewFieldValue"
            )[1].text
            hours = info_elements.find_elements(By.CLASS_NAME, "viewFieldValue")[2].text

            description_raw = self.driver.find_element(
                By.CSS_SELECTOR, "div.jobDesc"
            ).get_attribute("innerHTML")
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


# For debug
# driver = webdriver.Chrome()
# aa = IndianaPacers(driver=driver)

# aa.open_site()
# jobs = aa.get_jobs_available()
# aa
# for job in jobs:
#     job_data = aa._scrape_job(job)
#     if job_data:
#         enriched_job = aa._enrich_and_format_job(job_data)


# aa._create_record(enriched_job)
