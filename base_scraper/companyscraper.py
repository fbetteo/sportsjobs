from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import time
import utils
import os
from pyairtable import Api

AIRTABLE_TOKEN = os.getenv("AIRTABLE_TOKEN")
AIRTABLE_BASE = os.getenv("AIRTABLE_BASE")
AIRTABLE_JOBS_TABLE = os.getenv("AIRTABLE_JOBS_TABLE")

api = Api(AIRTABLE_TOKEN)
table = api.table(AIRTABLE_BASE, AIRTABLE_JOBS_TABLE)
KEYWORDS = [
    "data",
    "engineer",
    "analyst",
    "scientist",
    "machine learning",
    "deep learning",
    "artificial intelligence",
    "analytics",
]
# COMPANY = "Atlanta Hawks"
# LOGO = [
#     {
#         "url": "https://upload.wikimedia.org/wikipedia/en/thumb/2/24/Atlanta_Hawks_logo.svg/200px-Atlanta_Hawks_logo.svg.png",
#         "filename": "atlantahawks.png",
#     }
# ]


class CompanyScraper:

    def __init__(self, driver=None, keywords=None, table=table):
        now = datetime.now()
        self.keywords = (
            keywords if keywords is not None else self.get_default_keywords()
        )
        self.table = table
        self.current_time = now.strftime("%Y-%m-%d")
        self.driver = driver
        self.company = None
        self.logo = [
            {
                "url": "",
                "filename": "",
            }
        ]
        self.base_url = ""
        self.recent_urls = utils.get_recent_urls()

    def get_default_keywords(self):
        return [
            "data",
            "engineer",
            "analyst",
            "scientist",
            "machine learning",
            "deep learning",
            "artificial intelligence",
            "analytics",
        ]

    def open_site(self):
        self.driver.get(self.base_url)

        pass
        # implement wait per company
        # try:
        #     WebDriverWait(driver, 10).until(
        #         EC.presence_of_element_located((By.CLASS_NAME, "css-19uc56f"))
        #     )
        # except:
        #     print("Failed to load job listings")
        #     driver.quit()
        #     exit()

    def get_jobs_available(self):
        pass
        # jobs_rows = []
        # jobs = [
        # job
        # for job in driver.find_elements(By.CLASS_NAME, "css-19uc56f")
        # if any(keyword in job.text.lower() for keyword in KEYWORDS)
        # ]

        # jobs_rows = [{"title": job.text, "url": job.get_attribute("href")} for job in jobs]

    def _create_record(self, job_data):
        record = {
            "Name": job_data.get("Name"),
            "validated": True,
            "Status": "Open",
            "Start date": self.current_time,
            "url": job_data.get("url"),
            "location": job_data.get("location"),
            "country": job_data.get("country"),
            "seniority": job_data.get("seniority"),
            "desciption": job_data.get("desciption"),
            "sport_list": job_data.get("sport_list"),
            "skills": job_data.get("skills"),
            "remote": job_data.get("remote"),
            "remote_office": job_data.get("remote_office"),
            "job_area": job_data.get("job_area"),
            "salary": job_data.get("salary"),
            "language": job_data.get("language", ["English"]),
            "company": job_data.get("company", self.company),
            "industry": job_data.get("industry"),
            "type": job_data.get("type", ["Permanent"]),
            "hours": job_data.get("hours"),
            "logo": self.logo,
            "logo_permanent_url": self.logo[0].get("url"),
            "SEO:Index": "1",
        }
        self.table.create(record)

    def _scrape_job(self, job):
        return {}

    def _enrich_and_format_job(self, job_data: dict):

        job = job_data.get("job")
        location_value = job_data.get("location_value")
        hours = job_data.get("hours")
        full_description = job_data.get("full_description")

        other_data = job_data.get("other_data", {})

        skills_required_format, all_skills_format = utils.get_skills_required(
            full_description
        )
        none_skill = len(skills_required_format) < 2

        # if (job["url"] in self.recent_urls) or (none_skill):
        #     return None

        country = utils.find_country(location_value)
        accepts_remote = utils.get_remote_status(
            full_description, location_value, job["title"]
        )
        hours = utils.get_hours(job["title"], full_description, hours)
        remote_office = utils.is_remote_global(full_description)
        job_area = utils.add_job_area(skills_required_format)
        seniority = utils.get_seniority_level(job["title"])
        industry = utils.add_industry(job["title"], full_description)
        sport_list = utils.add_sport_list(job["title"], full_description)

        return {
            "Name": job["title"],
            "url": job["url"],
            "location": location_value,
            "country": country,
            "seniority": seniority,
            "desciption": full_description,
            "sport_list": sport_list,
            "skills": all_skills_format,
            "remote": accepts_remote,
            "remote_office": remote_office,
            "job_area": job_area,
            "salary": None,
            "industry": industry,
            "hours": [hours],
        } | other_data

    def _scrape_jobs(self, jobs):
        for job in jobs:
            job_data = self._scrape_job(job)
            if job_data:
                enriched_job = self._enrich_and_format_job(job_data)
                if enriched_job is not None:
                    self._create_record(enriched_job)
                else:
                    print(f"Job {job['title']} was not created")

    def main(self):
        self.open_site()
        jobs = self.get_jobs_available()
        self._scrape_jobs(jobs)


asd = {"a": 1, "b": 2}
dd = {"c": 3, "d": 4}

asd | {}
asd
# # Set up the Selenium WebDriver (assuming you're using Chrome)
# # driver_path = '/path/to/chromedriver'  # Update this with your actual path
# driver = webdriver.Chrome()

# # Open the Workday job site
# driver.get("https://wd1.myworkdaysite.com/en-US/recruiting/hawks/External")

# # Wait for the job listings to load (adjust the waiting time if necessary)
# try:
#     WebDriverWait(driver, 10).until(
#         EC.presence_of_element_located((By.CLASS_NAME, "css-19uc56f"))
#     )
# except:
#     print("Failed to load job listings")
#     driver.quit()
#     exit()

# # Scroll down to load more jobs (adjust the range as necessary)
# # for _ in range(5):  # Adjust range for more scrolls
# #     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
# #     time.sleep(2)  # Adjust sleep time if necessary

# # Parse the page source with BeautifulSoup
# # soup = BeautifulSoup(driver.page_source, 'html.parser')

# jobs_rows = []
# jobs = [
#     job
#     for job in driver.find_elements(By.CLASS_NAME, "css-19uc56f")
#     if any(keyword in job.text.lower() for keyword in KEYWORDS)
# ]

# jobs_rows = [{"title": job.text, "url": job.get_attribute("href")} for job in jobs]


# recent_urls = utils.get_recent_urls()

# for job in jobs_rows:
#     try:
#         # Extract job details
#         driver.get(job["url"])
#         WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.CLASS_NAME, "css-cygeeu"))
#         )

#         location_div = driver.find_element(By.CLASS_NAME, "css-cygeeu")
#         location_value = location_div.find_element(By.CLASS_NAME, "css-129m7dg").text

#         time_div = driver.find_element(By.CSS_SELECTOR, '[data-automation-id="time"]')
#         hours = time_div.find_element(By.CLASS_NAME, "css-129m7dg").text

#         description_raw = driver.find_element(
#             By.CSS_SELECTOR, '[data-automation-id="jobPostingDescription"]'
#         ).text
#         soup = BeautifulSoup(description_raw, "html.parser")
#         description = soup.get_text(separator="\n").strip()
#         full_description = f"{description}"

#         skills_required_format, all_skills_format = utils.get_skills_required(
#             full_description
#         )
#         none_skill = len(skills_required_format) < 2

#         if (job["url"] in recent_urls) or (none_skill):
#             continue

#         country = utils.find_country(location_value)
#         accepts_remote = utils.get_remote_status(
#             full_description, location_value, job["title"]
#         )
#         hours = utils.get_hours(job["title"], full_description, hours)
#         remote_office = utils.is_remote_global(full_description)
#         job_area = utils.add_job_area(skills_required_format)
#         seniority = utils.get_seniority_level(job["title"])
#         industry = utils.add_industry(job["title"], full_description)
#         sport_list = utils.add_sport_list(job["title"], full_description)

#         record = {
#             "Name": job["title"],
#             "validated": True,
#             "Status": "Open",
#             "Start date": current_time,
#             "url": job["url"],
#             "location": location_value,
#             "country": country,
#             "seniority": seniority,
#             "desciption": full_description,
#             "sport_list": sport_list,
#             "skills": all_skills_format,
#             "remote": accepts_remote,
#             "remote_office": remote_office,
#             "job_area": job_area,
#             "salary": None,
#             "language": ["English"],
#             "company": COMPANY,
#             "industry": industry,
#             "type": ["Permanent"],
#             "hours": [hours],
#             "logo": LOGO,
#             "logo_permanent_url": LOGO[0].get("url"),
#             "SEO:Index": "1",
#         }
#         table.create(record)

#         # WE GET THIS FROM THE JOB POSTING
#         # hours = utils.get_hours(job["title"], full_description)

#         # event_day = event.find_element(By.CSS_SELECTOR, "div.UIaQzd").text
#         # event_month = event.find_element(By.CSS_SELECTOR, "div.wsnHcb").text
#         # img_elements = event.find_element(By.TAG_NAME, "img").get_attribute(
#         #     "src"
#         # )

#         # # Extract the src attributes
#         # # src_list = [img.get_attribute("src") for img in img_elements]
#         # event_list.append(
#         #     {
#         #         "title": title,
#         #         "event_day": event_day,
#         #         "event_month": event_month,
#         #         "event_data": event_data,
#         #         "img": img_elements,
#         #     }
#         # )
#     except Exception as e:
#         print(f"Error extracting event: {e}")


# # Close the driver
# driver.quit()
