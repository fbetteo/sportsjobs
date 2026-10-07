import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import base_scraper.companyscraper
import base_scraper.teamworkonline
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


class NHL_Teamworkonline(base_scraper.teamworkonline.TeamworkOnlineScraper):
    company_from_job_page = True
    title_suffix = " - NHL"

    def __init__(self, driver=None, keywords=None):
        super().__init__(driver=driver, keywords=keywords)
        self.company = ""
        self.logo = [
            {
                "url": "",
                "filename": "",
            }
        ]
        self.base_url = ""


class BostonBruins(base_scraper.companyscraper.CompanyScraper):
    pass
    # Implement


class CalgaryFlames(base_scraper.companyscraper.CompanyScraper):

    def __init__(self, driver=None, keywords=None):
        super().__init__(driver=driver, keywords=keywords)
        self.company = "Calgary Flames"
        self.logo = [
            {
                "url": "https://upload.wikimedia.org/wikipedia/en/thumb/6/61/Calgary_Flames_logo.svg/220px-Calgary_Flames_logo.svg.png",
                "filename": "calgaryfalmes.png",
            }
        ]
        self.base_url = "https://recruiting.ultipro.ca/CAL5002/JobBoard/5f9649eb-fe0e-95eb-07f5-9ac9b3ae6647/?q=&o=postedDateDesc"

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
            raise Exception("Failed to load  job listings") 

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

            description_div = self.driver.find_element(
                By.CSS_SELECTOR, "p[data-automation='job-description']"
            )

            description_raw = description_div.get_attribute("innerHTML")

            full_description = markdownify.markdownify(
                description_raw, heading_style="ATX"
            )
            # soup = BeautifulSoup(description_raw, "html.parser")
            # description = soup.get_text(separator="\n").strip()
            # full_description = f"{description}"

            return {
                "job": job,
                "location_value": location_value,
                "hours": hours,
                "full_description": full_description,
            }
        except Exception as e:
            print(f"Error extracting event: {e}")
            return None


class MontrealCanadiens(base_scraper.companyscraper.CompanyScraper):
    pass
    # Implement


class NewYorkRangers(base_scraper.companyscraper.CompanyScraper):
    pass
    # Implemented in MSG greenhouse


class OttawaSenators(base_scraper.companyscraper.CompanyScraper):
    pass
    # Implement


class TorontoMapleLeafs(base_scraper.companyscraper.CompanyScraper):
    pass
    # uses smartrecruiters. Implement later, nothing interesting.


class VancouverCanucks(base_scraper.companyscraper.CompanyScraper):

    def __init__(self, driver=None, keywords=None):
        super().__init__(driver=driver, keywords=keywords)
        self.company = "Vancouver Canucks"
        self.logo = [
            {
                "url": "https://upload.wikimedia.org/wikipedia/en/thumb/3/3a/Vancouver_Canucks_logo.svg/220px-Vancouver_Canucks_logo.svg.png",
                "filename": "vancouvercanucks.png",
            }
        ]
        self.base_url = "https://recruiting.ultipro.ca/CAN5003AQG/JobBoard/ef431574-c057-4f55-95ac-f11092acb8de/?q=&o=postedDateDesc"

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
            raise Exception("Failed to load  job listings") 

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

            description_div = self.driver.find_element(
                By.CSS_SELECTOR, "p[data-automation='job-description']"
            )

            description_raw = description_div.get_attribute("innerHTML")

            full_description = markdownify.markdownify(
                description_raw, heading_style="ATX"
            )
            # soup = BeautifulSoup(description_raw, "html.parser")
            # description = soup.get_text(separator="\n").strip()
            # full_description = f"{description}"

            return {
                "job": job,
                "location_value": location_value,
                "hours": hours,
                "full_description": full_description,
            }
        except Exception as e:
            print(f"Error extracting event: {e}")
            return None


class WinnipegJets(base_scraper.companyscraper.CompanyScraper):
    pass
    # Implement


chrome_options = Options()
# required with the current docker image
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--remote-debugging-port=9222")
chrome_options.add_argument("--disable-gpu")

driver = webdriver.Chrome(options=chrome_options)

page = 0
# usually less than 3 motnhs ago
while page < 4:
    page += 1
    # try:
    print(f"Running TeamworkOnline page {page} ")
    team_instance = NHL_Teamworkonline(driver=driver)
    team_instance.base_url = f"https://www.teamworkonline.com/hockey-jobs/hockeyjobs/nhl-league-office?page={page}"
    team_instance.main()

teams = [
    CalgaryFlames,
    VancouverCanucks,
]

for team in teams:
    # try:
    print(f"Running {team.__name__} main()")
    team_instance = team(driver=driver)
    team_instance.main()
driver.quit()



# driver = webdriver.Chrome(options=chrome_options)
# aa = VancouverCanucks(driver=driver)

# aa.open_site()
# jobs = aa.get_jobs_available()

# for job in jobs[0:1]:
#     job_data = aa._scrape_job(job)