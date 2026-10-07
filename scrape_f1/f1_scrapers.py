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


class FormulaOne(base_scraper.companyscraper.CompanyScraper):

    def __init__(self, driver=None, keywords=None):
        super().__init__(driver=driver, keywords=keywords)
        self.company = "Formula 1"
        self.logo = [
            {
                "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2d/Formula_One_logo.svg/330px-Formula_One_logo.svg.png",
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
            raise Exception(
                "Failed to load TeamworkOnline job listings"
            )  # Raise exception instead of exit

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
            ).get_attribute("innerHTML")

            full_description = markdownify.markdownify(
                description_raw, heading_style="ATX"
            )

            # soup = BeautifulSoup(description_raw, "html.parser")
            # description = soup.get_text(separator="\n").strip()
            # full_description = f"{description}"

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

    # The CSS-module class names carry a build hash (e.g. "...__Jlg05W__vacancies__row"),
    # so match on the stable suffix only.
    ROW_SELECTOR = "[class*='vacancies__row']"
    TITLE_SELECTOR = "[class*='vacancies__title']"
    DETAILS_SELECTOR = "[class*='vacancies__details']"

    def open_site(self):
        self.driver.get(self.base_url)
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.ROW_SELECTOR))
            )
        except:
            print("Failed to load job listings")
            raise Exception(
                "Failed to load  job listings"
            )  # Raise exception instead of exit

    def get_jobs_available(self):
        jobs_rows = []
        for row in self.driver.find_elements(By.CSS_SELECTOR, self.ROW_SELECTOR):
            # Rows are hidden until a slide-in animation runs, so .text is empty.
            title = (
                row.find_element(By.CSS_SELECTOR, self.TITLE_SELECTOR)
                .get_attribute("textContent")
                .strip()
            )
            if any(keyword in title.lower() for keyword in self.keywords):
                url = row.find_element(
                    By.CSS_SELECTOR, "a[href*='/careers/vacancies/']"
                ).get_attribute("href")
                jobs_rows.append({"title": title, "url": url})
        return jobs_rows

    def _scrape_job(self, job):
        try:
            # Extract job details
            self.driver.get(job["url"])
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, self.DETAILS_SELECTOR)
                )
            )

            location_value = "Brackley, United Kingdom"
            hours = "Full-time"

            description_raw = self.driver.find_element(
                By.CSS_SELECTOR, self.DETAILS_SELECTOR
            ).get_attribute("innerHTML")

            full_description = markdownify.markdownify(
                description_raw, heading_style="ATX"
            )

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
        # Attrax careers site; /jobs lists every opening as a vacancy tile.
        self.base_url = "https://racingcareers.mclaren.com/jobs"

    def open_site(self):
        self.driver.get(self.base_url)
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "a.attrax-vacancy-tile__title")
                )
            )
        except:
            print("Failed to load job listings")
            raise Exception("Failed to load  job listings")

    def get_jobs_available(self):
        jobs_rows = []
        for tile in self.driver.find_elements(By.CLASS_NAME, "attrax-vacancy-tile"):
            link = tile.find_element(By.CSS_SELECTOR, "a.attrax-vacancy-tile__title")
            title = link.text
            if not any(keyword in title.lower() for keyword in self.keywords):
                continue
            locations = tile.find_elements(
                By.CSS_SELECTOR,
                ".attrax-vacancy-tile__location-freetext .attrax-vacancy-tile__item-value",
            )
            jobs_rows.append(
                {
                    "title": title,
                    "url": link.get_attribute("href"),
                    # Full "City, Region, Country" text; the job page only shows the city.
                    "location": locations[0].text if locations else "",
                }
            )
        return jobs_rows

    def _scrape_job(self, job):
        try:
            # Extract job details
            self.driver.get(job["url"])
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "description-widget"))
            )

            location_value = job.get("location") or "Woking, United Kingdom"
            hours = "Full-time"

            description_raw = self.driver.find_element(
                By.CLASS_NAME, "description-widget"
            ).get_attribute("innerHTML")

            full_description = markdownify.markdownify(
                description_raw, heading_style="ATX"
            )

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
            raise Exception("Failed to load  job listings")

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
            ).get_attribute("innerHTML")

            full_description = markdownify.markdownify(
                description_raw, heading_style="ATX"
            )

            # soup = BeautifulSoup(description_raw, "html.parser")
            # description = soup.get_text(separator="\n").strip()
            # full_description = f"{description}"

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
            raise Exception("Failed to load  job listings")

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
            raise Exception("Failed to load  job listings")

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
            ).get_attribute("innerHTML")

            full_description = markdownify.markdownify(
                description_raw, heading_style="ATX"
            )

            # soup = BeautifulSoup(description_raw, "html.parser")
            # description = soup.get_text(separator="\n").strip()
            # full_description = f"{description}"

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
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--remote-debugging-port=9222")
chrome_options.add_argument("--disable-gpu")

driver = webdriver.Chrome(options=chrome_options)
teams = [
    Mclaren,
    Mercedes,
    RedBull,
    Haas,
    Williams,
    # Alpine,
    # Ferrari,
    # AstonMartin,
    FormulaOne,
]

for team in teams:
    # try:
    print(f"Running {team.__name__} main()")
    team_instance = team(driver=driver)
    team_instance.main()
driver.quit()
