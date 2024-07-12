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


class LosAngelesClippers(base_scraper.companyscraper.CompanyScraper):
    # I get it from greenhouse
    pass


class LosAngelesLakers(base_scraper.companyscraper.CompanyScraper):

    def __init__(self, driver=None, keywords=None):
        super().__init__(driver=driver, keywords=keywords)
        self.company = "Los Angeles Lakers"
        self.logo = [
            {
                "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3c/Los_Angeles_Lakers_logo.svg/220px-Los_Angeles_Lakers_logo.svg.png",
                "filename": "lalakers.png",
            }
        ]
        self.base_url = "https://www.teamworkonline.com/basketball-jobs/los-angeles-lakers/los-angeles-lakers-jobs"

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


class MemphisGrizzlies(base_scraper.companyscraper.CompanyScraper):

    def __init__(self, driver=None, keywords=None):
        super().__init__(driver=driver, keywords=keywords)
        self.company = "Memphis Grizzlies"
        self.logo = [
            {
                "url": "https://upload.wikimedia.org/wikipedia/en/thumb/f/f1/Memphis_Grizzlies.svg/190px-Memphis_Grizzlies.svg.png",
                "filename": "memphisgrizzlies.png",
            }
        ]
        self.base_url = "https://careers-grizzlies.icims.com/jobs/search?ss=1&searchKeyword=&searchCategory=&searchZip=&searchRadius=20"

        # COULDN'T FIND ANYTHING
        pass


class MiamiHeat(base_scraper.companyscraper.CompanyScraper):

    def __init__(self, driver=None, keywords=None):
        super().__init__(driver=driver, keywords=keywords)
        self.company = "Miami Heat"
        self.logo = [
            {
                "url": "https://upload.wikimedia.org/wikipedia/en/thumb/f/fb/Miami_Heat_logo.svg/200px-Miami_Heat_logo.svg.png",
                "filename": "miamiheat.png",
            }
        ]
        self.base_url = "https://recruiting.ultipro.com/MIA1004MHLP/JobBoard/b34868a3-6ce1-4a28-b8fb-afb1cd5be9d3/?q=&o=postedDateDesc"

    def open_site(self):
        self.driver.get(self.base_url)
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "a[data-automation='job-title']")
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
                By.CSS_SELECTOR, "a[data-automation='job-title']"
            )
            if any(keyword in job.text.lower() for keyword in self.keywords)
        ]

        jobs_rows = [
            {
                "title": job.text,
                "url": job.get_attribute("href"),
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
                    (By.CSS_SELECTOR, "h3[data-automation='descriptions-title']")
                )
            )

            location_value = self.driver.find_element(
                By.CSS_SELECTOR, "span[data-automation='city-state-zip-country-label']"
            ).text

            hours = self.driver.find_element(
                By.CSS_SELECTOR, "span[data-automation='JobFullTime']"
            ).text

            description_raw = self.driver.find_element(
                By.CSS_SELECTOR, "p[data-automation='job-description']"
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


class MilwaukeeBucks(base_scraper.companyscraper.CompanyScraper):
    # Use this site (used to work, not now)
    # https://careers-bucks.icims.com/jobs/intro?mobile=false&width=1250&height=500&bga=true&needsRedirect=false&jan1offset=-300&jun1offset=-240
    pass


class MinnesotaTimberwolves(base_scraper.companyscraper.CompanyScraper):

    def __init__(self, driver=None, keywords=None):
        super().__init__(driver=driver, keywords=keywords)
        self.company = "Minnesota Timberwolves"
        self.logo = [
            {
                "url": "https://upload.wikimedia.org/wikipedia/en/thumb/c/c2/Minnesota_Timberwolves_logo.svg/200px-Minnesota_Timberwolves_logo.svg.png",
                "filename": "minnesotatimberwolves.png",
            }
        ]
        self.base_url = "https://jobs.dayforcehcm.com/en-US/packportal/CANDIDATEPORTAL"

    def open_site(self):
        self.driver.get(self.base_url)
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "li.ant-list-item"))
            )
        except:
            print("Failed to load job listings")
            exit()

    def get_jobs_available(self):
        jobs_rows = []
        jobs = [
            job
            for job in self.driver.find_elements(By.CSS_SELECTOR, "li.ant-list-item")
            if any(
                keyword
                in job.find_element(By.CSS_SELECTOR, "a.inline-block.max-w-full")
                .find_element(By.TAG_NAME, "h2")
                .text.lower()
                for keyword in self.keywords
            )
        ]

        jobs_rows = [
            {
                "title": job.find_element(By.CSS_SELECTOR, "a.inline-block.max-w-full")
                .find_element(By.TAG_NAME, "h2")
                .text,
                "url": job.find_element(
                    By.CSS_SELECTOR, "a.inline-block.max-w-full"
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
                    (By.CSS_SELECTOR, "div[test-id='job-detail-body']")
                )
            )

            location_value = self.driver.find_element(
                By.CSS_SELECTOR, 'span[test-id="job-detail-location-name"]'
            ).text

            hours = "Full-time"

            description_raw = self.driver.find_element(
                By.CSS_SELECTOR, "div[test-id='job-detail-body']"
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


class NewOrleansPelicans(base_scraper.companyscraper.CompanyScraper):

    def __init__(self, driver=None, keywords=None):
        super().__init__(driver=driver, keywords=keywords)
        self.company = "New Orleans Pelicans / Saints"
        self.logo = [
            {
                "url": "https://upload.wikimedia.org/wikipedia/en/thumb/0/0d/New_Orleans_Pelicans_logo.svg/250px-New_Orleans_Pelicans_logo.svg.png",
                "filename": "neworleanspelicans.png",
            }
        ]
        self.base_url = "https://us241.dayforcehcm.com/CandidatePortal/en-US/bensonenterprises/SITE/SAINTSPELSCAREERS"

    def open_site(self):
        self.driver.get(self.base_url)
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "ul.search-results li.search-result")
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
                By.CSS_SELECTOR, "ul.search-results li.search-result"
            )
            if any(
                keyword
                in job.find_element(
                    By.CSS_SELECTOR, "div.posting-title h2 a"
                ).text.lower()
                for keyword in self.keywords
            )
        ]

        jobs_rows = [
            {
                "title": job.find_element(
                    By.CSS_SELECTOR, "div.posting-title h2 a"
                ).text,
                "url": job.find_element(
                    By.CSS_SELECTOR, "div.posting-title h2 a"
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
                    (By.CSS_SELECTOR, "div.job-posting-content")
                )
            )

            location_value = self.driver.find_element(
                By.CSS_SELECTOR, "span.job-location"
            ).text

            hours = "Full-time"

            description_raw = self.driver.find_element(
                By.CSS_SELECTOR, "div.job-posting-content"
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


class NewYorkKnicks(base_scraper.companyscraper.CompanyScraper):
    pass
    ## I get it from greenhouse as MSGSPORTS


class OklahomaThunder(base_scraper.companyscraper.CompanyScraper):

    def __init__(self, driver=None, keywords=None):
        super().__init__(driver=driver, keywords=keywords)
        self.company = "Oklahoma City Thunder"
        self.logo = [
            {
                "url": "https://upload.wikimedia.org/wikipedia/en/thumb/5/5d/Oklahoma_City_Thunder.svg/200px-Oklahoma_City_Thunder.svg.png",
                "filename": "okcthunder.png",
            }
        ]
        self.base_url = "https://www.nba.com/thunder/employment"

    def open_site(self):
        self.driver.get(self.base_url)
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        'div.Columns_column__dIKLJ div[data-testid="paragraph"] p.has-text-align-center a',
                    )
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
                By.CSS_SELECTOR,
                'div.Columns_column__dIKLJ div[data-testid="paragraph"] p.has-text-align-center a',
            )
            if any(keyword in job.text.lower() for keyword in self.keywords)
        ]

        jobs_rows = [
            {
                "title": job.text,
                "url": job.get_attribute("href"),
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
                    (By.CSS_SELECTOR, 'div[data-testid="group"]')
                )
            )

            location_value = "208 Thunder Drive Oklahoma City, OK 73102"

            hours = "Full-time"

            job_description_container = self.driver.find_element(
                By.CSS_SELECTOR, 'div[data-testid="group"]'
            )
            description_elements = job_description_container.find_elements(
                By.XPATH, ".//*"
            )

            # Concatenate the text content of all paragraph elements
            description_raw = "\n".join(
                [
                    element.text
                    for element in description_elements
                    if element.text.strip() != ""
                ]
            )

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


class OrlandoMagic(base_scraper.companyscraper.CompanyScraper):

    def __init__(self, driver=None, keywords=None):
        super().__init__(driver=driver, keywords=keywords)
        self.company = "Orlando Magic"
        self.logo = [
            {
                "url": "https://upload.wikimedia.org/wikipedia/en/thumb/1/10/Orlando_Magic_logo.svg/220px-Orlando_Magic_logo.svg.png",
                "filename": "orlandomagic.png",
            }
        ]
        self.base_url = "https://recruiting.ultipro.com/ORL1001MAGIC/JobBoard/d2d331e7-e222-4a47-bb35-c640aa29a3d7/?q=&o=postedDateDesc"

    def open_site(self):
        self.driver.get(self.base_url)
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "a[data-automation='job-title']")
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
                By.CSS_SELECTOR, "a[data-automation='job-title']"
            )
            if any(keyword in job.text.lower() for keyword in self.keywords)
        ]

        jobs_rows = [
            {
                "title": job.text,
                "url": job.get_attribute("href"),
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
                    (By.CSS_SELECTOR, "h3[data-automation='descriptions-title']")
                )
            )

            location_value = self.driver.find_element(
                By.CSS_SELECTOR, "span[data-automation='city-state-zip-country-label']"
            ).text

            hours = self.driver.find_element(
                By.CSS_SELECTOR, "span[data-automation='JobFullTime']"
            ).text

            description_raw = self.driver.find_element(
                By.CSS_SELECTOR, "p[data-automation='job-description']"
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


class Philadelphia76ers(base_scraper.companyscraper.CompanyScraper):
    pass
    # Need to implement HireBr


###########
# For debug
# driver = webdriver.Chrome()
# aa = OrlandoMagic(driver=driver)

# aa.open_site()
# jobs = aa.get_jobs_available()
# # gasta aca vamos bien, ver si no conviene greenhouse o alguna para cada equipo
# # aa
# for job in jobs[0:1]:
#     job_data = aa._scrape_job(job)
#     if job_data:
#         enriched_job = aa._enrich_and_format_job(job_data)


# aa._create_record(enriched_job)


chrome_options = Options()
# required with the current docker image
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--remote-debugging-port=9222")

driver = webdriver.Chrome(options=chrome_options)
teams = [DetroitPistons, GoldenStateWarriors, HoustonRockets, IndianaPacers]

for team in teams:
    # try:
    print(f"Running {team.__name__} main()")
    team_instance = team(driver=driver)
    team_instance.main()
# except Exception as e:
#     print(f"Error running {team.__name__} main(): {e}")
