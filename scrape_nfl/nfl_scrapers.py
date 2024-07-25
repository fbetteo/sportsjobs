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


class NFL_Teamworkonline(base_scraper.companyscraper.CompanyScraper):

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


class PhiladelphiaEagles(base_scraper.companyscraper.CompanyScraper):
    pass
    # Greenhouse


class SanFrancisco49ers(base_scraper.companyscraper.CompanyScraper):
    pass
    # Implement


class SeattleSeahawks(base_scraper.companyscraper.CompanyScraper):

    def __init__(self, driver=None, keywords=None):
        super().__init__(driver=driver, keywords=keywords)
        self.company = "Seattle Seahawks"
        self.logo = [
            {
                "url": "https://static.www.nfl.com/t_q-best/league/api/clubs/logos/SEA",
                "filename": "seattleseahawks.png",
            }
        ]
        self.base_url = "https://www2.seahawks.com/employment/openings/"

    def open_site(self):
        self.driver.get(self.base_url)
        # I can't get this to work
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "menu_table"))
            )
        except:
            print("Failed to load job listings")
            exit()

    def get_jobs_available(self):
        jobs_rows = []
        jobs = [
            job
            for job in self.driver.find_elements(By.CSS_SELECTOR, "tr[id^='row_job_']")
            if any(
                keyword
                in job.find_element(By.CLASS_NAME, "job_title_link").text.lower()
                for keyword in self.keywords
            )
        ]

        jobs_rows = [
            {
                "title": job.find_element(By.CLASS_NAME, "job_title_link").text,
                "url": job.find_element(By.CLASS_NAME, "job_title_link").get_attribute(
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
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.job_header"))
            )

            job_header = self.driver.find_element(By.CSS_SELECTOR, "div.job_header")
            job_info = job_header.find_element(By.CSS_SELECTOR, "h3.job_meta").text
            location_value = job_info.rsplit(" - ", 1)[0]

            hours = job_info.rsplit(" - ", 1)[1]

            description_raw = self.driver.find_element(
                By.CLASS_NAME, "job_description"
            ).get_attribute("innerHTML")

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


class TampaBayBuccaneers(base_scraper.companyscraper.CompanyScraper):

    def __init__(self, driver=None, keywords=None):
        super().__init__(driver=driver, keywords=keywords)
        self.company = "Tampa Bay Buccaneers"
        self.logo = [
            {
                "url": "https://jobs.dayforcehcm.com/_next/image?url=https%3A%2F%2Fus241.dayforcehcm.com%2FCandidatePortal%2Fen-US%2Ftbb%2FGo%3Fitem%3D7ca555bb-c07d-4855-8d5a-0c23159e629f&w=1920&q=75",
                "filename": "tampabaybuccaneers.png",
            }
        ]
        self.base_url = "https://jobs.dayforcehcm.com/en-US/tbb/CANDIDATEPORTALTBB"

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


class BaltimoreRavens(base_scraper.companyscraper.CompanyScraper):

    def __init__(self, driver=None, keywords=None):
        super().__init__(driver=driver, keywords=keywords)
        self.company = "Baltimore Ravens"
        self.logo = [
            {
                "url": "https://us241.dayforcehcm.com/CandidatePortal/en-US/baltimoreravens/CPBrandingLogo?item=c21c20a6-e3f8-42a7-b30a-bf9a6b090304",
                "filename": "baltimoreravens.png",
            }
        ]
        self.base_url = (
            "https://us241.dayforcehcm.com/CandidatePortal/en-US/baltimoreravens"
        )

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
            ).get_attribute("innerHTML")

            full_description = markdownify.markdownify(
                description_raw, heading_style="ATX"
            )
            # soup = BeautifulSoup(description_raw, "html.parser")
            # description = soup.get_text(separator="\n").strip()
            # full_description = f"{description}"

            job["title"] += " - NFL"

            return {
                "job": job,
                "location_value": location_value,
                "hours": hours,
                "full_description": full_description,
            }
        except Exception as e:
            print(f"Error extracting event: {e}")
            return None


class ChicagoBears(base_scraper.companyscraper.CompanyScraper):
    pass
    # Implement


class LosAngelesChargers(base_scraper.companyscraper.CompanyScraper):
    pass
    # Implement Linkedin


class NewEnglandPatriots(base_scraper.companyscraper.CompanyScraper):
    pass
    # Implement


class NewOrleansSaints(base_scraper.companyscraper.CompanyScraper):
    pass
    # Implemented in the nba, they share site with neworleanspelicans


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
    team_instance = NFL_Teamworkonline(driver=driver)
    team_instance.base_url = f"https://www.teamworkonline.com/football-jobs/footballjobs/nfl-football-jobs?employment_opportunity_search%5Bcareer_level_id%5D=&employment_opportunity_search%5Bcategory_id%5D=&employment_opportunity_search%5Borganization_id%5D=&employment_opportunity_search%5Bquery%5D=&page={page}"
    team_instance.main()

teams = [
    # PhiladelphiaEagles,
    # SanFrancisco49ers,
    # SeattleSeahawks, # Not working
    TampaBayBuccaneers,
    BaltimoreRavens,
    # ChicagoBears,
    # LosAngelesChargers,
    # NewEnglandPatriots,
    # NewOrleansSaints,
]

for team in teams:
    # try:
    print(f"Running {team.__name__} main()")
    team_instance = team(driver=driver)
    team_instance.main()
driver.quit()
