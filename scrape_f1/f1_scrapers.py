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


class FormulaOne(base_scraper.companyscraper.CompanyScraper):

    def __init__(self, driver=None, keywords=None):
        super().__init__(driver=driver, keywords=keywords)
        self.company = "Formula 1"
        self.logo = [
            {
                "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0d/F1_%28registered_trademark%29.svg/250px-F1_%28registered_trademark%29.svg.png",
                "filename": "formulaone.png",
            }
        ]
        self.base_url = "https://formulaone.wd3.myworkdayjobs.com/F1/"

    def open_site(self):
        self.driver.get(self.base_url)
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "css-19uc56f"))
            )
        except:
            print("Failed to load job listings")
            exit()

    def get_jobs_available(self):
        jobs_rows = []
        jobs = [
            job
            for job in self.driver.find_elements(By.CLASS_NAME, "css-19uc56f")
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
                EC.presence_of_element_located((By.CLASS_NAME, "css-cygeeu"))
            )

            info_elements = self.driver.find_elements(
                By.CLASS_NAME, "opportunity-preview__info-content-item"
            )
            location_div = self.driver.find_element(By.CLASS_NAME, "css-cygeeu")
            location_value = location_div.find_element(
                By.CLASS_NAME, "css-129m7dg"
            ).text

            time_div = self.driver.find_element(
                By.CSS_SELECTOR, '[data-automation-id="time"]'
            )
            hours = time_div.find_element(By.CLASS_NAME, "css-129m7dg").text

            description_raw = self.driver.find_element(
                By.CSS_SELECTOR, '[data-automation-id="jobPostingDescription"]'
            ).text

            soup = BeautifulSoup(description_raw, "html.parser")
            description = soup.get_text(separator="\n").strip()
            full_description = f"{description}"

            job["title"] += " - Formula1"

            return {
                "job": job,
                "location_value": location_value,
                "hours": hours,
                "full_description": full_description,
            }
        except Exception as e:
            print(f"Error extracting event: {e}")
            return None


class Mercedes(base_scraper.companyscraper.CompanyScraper):

    def __init__(self, driver=None, keywords=None):
        super().__init__(driver=driver, keywords=keywords)
        self.company = "Mercedes"
        self.logo = [
            {
                "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Mercedes-Benz_in_Formula_One_logo.svg/220px-Mercedes-Benz_in_Formula_One_logo.svg.png",
                "filename": "mercedes.png",
            }
        ]
        self.base_url = "https://www.mercedesamgf1.com/careers/vacancies"

    def open_site(self):
        self.driver.get(self.base_url)
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, "vacancylist_vacancies__row__gHcKz")
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
                By.CLASS_NAME, "vacancylist_vacancies__row__gHcKz"
            )
            if any(
                keyword
                in job.find_element(
                    By.CLASS_NAME, "vacancylist_vacancies__title__YvFkz"
                ).text.lower()
                for keyword in self.keywords
            )
        ]

        jobs_rows = [
            {
                "title": job.find_element(
                    By.CLASS_NAME, "vacancylist_vacancies__title__YvFkz"
                ).text,
                "url": job.find_element(
                    By.CSS_SELECTOR, "a.btn.btn--primary.slide-animation.full-xs"
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
                    (By.CLASS_NAME, "vacancylist_vacancies__details__jIOyz")
                )
            )

            location_value = "Brackley, United Kingdom"
            hours = "Full-time"

            description_raw = driver.find_element(
                By.CLASS_NAME, "vacancylist_vacancies__details__jIOyz"
            ).get_attribute("innerHTML")

            soup = BeautifulSoup(description_raw, "html.parser")
            description = soup.get_text(separator="\n").strip()
            full_description = f"{description}"

            job["title"] += " - Formula1"

            return {
                "job": job,
                "location_value": location_value,
                "hours": hours,
                "full_description": full_description,
            }
        except Exception as e:
            print(f"Error extracting event: {e}")
            return None


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

            job["title"] += " - Formula1"

            return {
                "job": job,
                "location_value": location_value,
                "hours": hours,
                "full_description": full_description,
            }
        except Exception as e:
            print(f"Error extracting event: {e}")
            return None


class RedBull(base_scraper.companyscraper.CompanyScraper):

    def __init__(self, driver=None, keywords=None):
        super().__init__(driver=driver, keywords=keywords)
        self.company = "Red Bull Racing"
        self.logo = [
            {
                "url": "https://upload.wikimedia.org/wikipedia/en/4/44/Red_bull_racing.png",
                "filename": "redbull.png",
            }
        ]
        self.base_url = (
            "https://redbulltechnology.wd3.myworkdayjobs.com/en-US/RB_Racing"
        )

    def open_site(self):
        self.driver.get(self.base_url)
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "css-19uc56f"))
            )
        except:
            print("Failed to load job listings")
            exit()

    def get_jobs_available(self):
        jobs_rows = []
        jobs = [
            job
            for job in self.driver.find_elements(By.CLASS_NAME, "css-19uc56f")
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
                EC.presence_of_element_located((By.CLASS_NAME, "css-cygeeu"))
            )

            # info_elements = self.driver.find_elements(
            #     By.CLASS_NAME, "opportunity-preview__info-content-item"
            # )
            location_div = self.driver.find_element(By.CLASS_NAME, "css-cygeeu")
            location_value = location_div.find_element(
                By.CLASS_NAME, "css-129m7dg"
            ).text

            time_div = self.driver.find_element(
                By.CSS_SELECTOR, '[data-automation-id="time"]'
            )
            hours = time_div.find_element(By.CLASS_NAME, "css-129m7dg").text

            description_raw = self.driver.find_element(
                By.CSS_SELECTOR, '[data-automation-id="jobPostingDescription"]'
            ).text

            soup = BeautifulSoup(description_raw, "html.parser")
            description = soup.get_text(separator="\n").strip()
            full_description = f"{description}"

            job["title"] += " - Formula1"

            return {
                "job": job,
                "location_value": location_value,
                "hours": hours,
                "full_description": full_description,
            }
        except Exception as e:
            print(f"Error extracting event: {e}")
            return None


class Haas(base_scraper.companyscraper.CompanyScraper):

    def __init__(self, driver=None, keywords=None):
        super().__init__(driver=driver, keywords=keywords)
        self.company = "Haas F1 Team"
        self.logo = [
            {
                "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/92/MoneyGram_Haas_F1_Team_Logo.svg/220px-MoneyGram_Haas_F1_Team_Logo.svg.png",
                "filename": "haasf1.png",
            }
        ]
        self.base_url = "https://haasf1team.bamboohr.com/careers"

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

            soup = BeautifulSoup(description_raw, "html.parser")
            description = soup.get_text(separator="\n").strip()
            full_description = f"{description}"

            job["title"] += " - Formula1"

            return {
                "job": job,
                "location_value": location_value,
                "hours": hours,
                "full_description": full_description,
            }
        except Exception as e:
            print(f"Error extracting event: {e}")
            return None


class AstonMartin(base_scraper.companyscraper.CompanyScraper):
    pass
    # own recruiting page and no useful job offers available


class Ferrari(base_scraper.companyscraper.CompanyScraper):

    pass


# own recruiting page and no useful job offers available


class Alpine(base_scraper.companyscraper.CompanyScraper):

    pass
    # own recruiting page and no useful job offers available


class Williams(base_scraper.companyscraper.CompanyScraper):

    def __init__(self, driver=None, keywords=None):
        super().__init__(driver=driver, keywords=keywords)
        self.company = "Williams Racing"
        self.logo = [
            {
                "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e8/Williams_Racing_2020_logo.png/220px-Williams_Racing_2020_logo.png",
                "filename": "williamsracing.png",
            }
        ]
        self.base_url = "https://alcority.wd1.myworkdayjobs.com/WilliamsRacing"

    def open_site(self):
        self.driver.get(self.base_url)
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "css-19uc56f"))
            )
        except:
            print("Failed to load job listings")
            exit()

    def get_jobs_available(self):
        jobs_rows = []
        jobs = [
            job
            for job in self.driver.find_elements(By.CLASS_NAME, "css-19uc56f")
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
                EC.presence_of_element_located((By.CLASS_NAME, "css-cygeeu"))
            )

            info_elements = self.driver.find_elements(
                By.CLASS_NAME, "opportunity-preview__info-content-item"
            )
            location_div = self.driver.find_element(By.CLASS_NAME, "css-cygeeu")
            location_value = location_div.find_element(
                By.CLASS_NAME, "css-129m7dg"
            ).text

            time_div = self.driver.find_element(
                By.CSS_SELECTOR, '[data-automation-id="time"]'
            )
            hours = time_div.find_element(By.CLASS_NAME, "css-129m7dg").text

            description_raw = self.driver.find_element(
                By.CSS_SELECTOR, '[data-automation-id="jobPostingDescription"]'
            ).text

            soup = BeautifulSoup(description_raw, "html.parser")
            description = soup.get_text(separator="\n").strip()
            full_description = f"{description}"

            job["title"] += " - Formula1"

            return {
                "job": job,
                "location_value": location_value,
                "hours": hours,
                "full_description": full_description,
            }
        except Exception as e:
            print(f"Error extracting event: {e}")
            return None


# # For debug
# driver = webdriver.Chrome()
# aa = Williams(driver=driver)

# aa.open_site()
# jobs = aa.get_jobs_available()

# for job in jobs[0:1]:
#     job_data = aa._scrape_job(job)

chrome_options = Options()
# required with the current docker image
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--remote-debugging-port=9222")

driver = webdriver.Chrome(options=chrome_options)
teams = [
    Mclaren,
    Mercedes,
    RedBull,
    Haas,
    Williams,
    Alpine,
    Ferrari,
    AstonMartin,
    FormulaOne,
]

for team in teams:
    # try:
    print(f"Running {team.__name__} main()")
    team_instance = team(driver=driver)
    team_instance.main()
driver.quit()
