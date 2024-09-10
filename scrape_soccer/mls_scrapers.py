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


class MLS_Teamworkonline(base_scraper.companyscraper.CompanyScraper):

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

            team_name_element = self.driver.find_element(
                By.CSS_SELECTOR, "div.lic-header__name > h1"
            )
            self.company = team_name_element.text

            # Locate the image element and extract the src attribute
            image_element = self.driver.find_element(
                By.CSS_SELECTOR,
                "div.lic-header__logo-wrap a.lic-header__logo-wrap--link > img",
            )
            self.logo[0]["url"] = image_element.get_attribute("src")
            self.logo[0]["filename"] = f"{self.company}.png"

            info_elements = self.driver.find_elements(
                By.CLASS_NAME, "opportunity-preview__info-content-item"
            )
            location_value = info_elements[1].text
            hours = info_elements[0].text

            description_raw = self.driver.find_element(
                By.CLASS_NAME, "opportunity-preview__body"
            ).get_attribute("innerHTML")

            full_description = markdownify.markdownify(
                description_raw, heading_style="ATX"
            )
            # soup = BeautifulSoup(description_raw, "html.parser")
            # description = soup.get_text(separator="\n").strip()
            # full_description = f"{description}"

            # to be sure the sport is identified in utils.add_sport_list()
            job["title"] += " - MLS"

            return {
                "job": job,
                "location_value": location_value,
                "hours": hours,
                "full_description": full_description,
                "other_data": {"sport_list": ["Football - Soccer"]},
            }
        except Exception as e:
            print(f"Error extracting event: {e}")
            return None


class DallasFC(base_scraper.companyscraper.CompanyScraper):
    pass


class MontrealFC(base_scraper.companyscraper.CompanyScraper):
    pass


class TorontoFC(base_scraper.companyscraper.CompanyScraper):
    pass


class VancouverWhitecaps(base_scraper.companyscraper.CompanyScraper):
    def __init__(self, driver=None, keywords=None):
        super().__init__(driver=driver, keywords=keywords)
        self.company = "Vancouver Whitecaps"
        self.logo = [
            {
                "url": "https://upload.wikimedia.org/wikipedia/en/thumb/5/5d/Vancouver_Whitecaps_FC_logo.svg/190px-Vancouver_Whitecaps_FC_logo.svg.png",
                "filename": "vancouverwhitecaps.png",
            }
        ]
        self.base_url = "https://whitecapsfc.bamboohr.com/careers"

    def open_site(self):
        self.driver.get(self.base_url)
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "fab-Card"))
            )
        except:
            print("Failed to load job listings")
            exit()

    def get_jobs_available(self):
        jobs_rows = []
        jobs = [
            job
            for job in self.driver.find_elements(By.CSS_SELECTOR, "li")
            if any(
                keyword in job.find_element(By.CSS_SELECTOR, "a.jss-f73").text.lower()
                for keyword in self.keywords
            )
        ]

        jobs_rows = [
            {
                "title": job.find_element(By.CSS_SELECTOR, "a.jss-f73").text,
                "url": job.find_element(By.CSS_SELECTOR, "a.jss-f73").get_attribute(
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
                EC.presence_of_element_located((By.ID, "descriptionWrapper"))
            )

            # Extract location
            location_elements = self.driver.find_elements(
                By.CSS_SELECTOR, ".jss-f78 p.jss-f76, .jss-f78 p.jss-f77"
            )
            location_value = ", ".join([elem.text for elem in location_elements])
            hours = "Full-time"
            # Extract job description HTML
            description_raw = self.driver.find_element(
                By.CLASS_NAME, "BambooRichText"
            ).get_attribute("innerHTML")

            full_description = markdownify.markdownify(
                description_raw, heading_style="ATX"
            )

            # soup = BeautifulSoup(description_raw, "html.parser")
            # description = soup.get_text(separator="\n").strip()
            # full_description = f"{description}"

            job["title"] += " - MLS"

            return {
                "job": job,
                "location_value": location_value,
                "hours": hours,
                "full_description": full_description,
                "other_data": {"sport_list": ["Football - Soccer"]},
            }
        except Exception as e:
            print(f"Error extracting event: {e}")
            return None


class NWSL_Teamworkonline(base_scraper.companyscraper.CompanyScraper):

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
            "https://www.teamworkonline.com/soccer-jobs/nwslsoccer/nwsl-league-office"
        )

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

            team_name_element = self.driver.find_element(
                By.CSS_SELECTOR, "div.lic-header__name > h1"
            )
            self.company = team_name_element.text

            # Locate the image element and extract the src attribute
            image_element = self.driver.find_element(
                By.CSS_SELECTOR,
                "div.lic-header__logo-wrap a.lic-header__logo-wrap--link > img",
            )
            self.logo[0]["url"] = image_element.get_attribute("src")
            self.logo[0]["filename"] = f"{self.company}.png"

            info_elements = self.driver.find_elements(
                By.CLASS_NAME, "opportunity-preview__info-content-item"
            )
            location_value = info_elements[1].text
            hours = info_elements[0].text

            description_raw = self.driver.find_element(
                By.CLASS_NAME, "opportunity-preview__body"
            ).get_attribute("innerHTML")

            full_description = markdownify.markdownify(
                description_raw, heading_style="ATX"
            )
            # soup = BeautifulSoup(description_raw, "html.parser")
            # description = soup.get_text(separator="\n").strip()
            # full_description = f"{description}"

            # to be sure the sport is identified in utils.add_sport_list()
            job["title"] += " - MLS"

            return {
                "job": job,
                "location_value": location_value,
                "hours": hours,
                "full_description": full_description,
                "other_data": {"sport_list": ["Football - Soccer"]},
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

page = 0
# usually less than 3 motnhs ago
while page < 4:
    page += 1
    # try:
    print(f"Running TeamworkOnline page {page} ")
    team_instance = MLS_Teamworkonline(driver=driver)
    team_instance.base_url = f"https://www.teamworkonline.com/soccer-jobs/mls/mls-league-office-soccer-united-marketing?page={page}"
    team_instance.main()

teams = [VancouverWhitecaps, NWSL_Teamworkonline]

for team in teams:
    # try:
    print(f"Running {team.__name__} main()")
    team_instance = team(driver=driver)
    team_instance.main()
driver.quit()
