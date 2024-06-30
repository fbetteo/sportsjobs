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
COMPANY = "Cleveland Cavaliers"
LOGO = [
    {
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Cleveland_Cavaliers_logo.svg/160px-Cleveland_Cavaliers_logo.svg.png",
        "filename": "clevelandcavaliers.png",
    }
]

now = datetime.now()
current_time = now.strftime("%Y-%m-%d")
# Set up the Selenium WebDriver (assuming you're using Chrome)
# driver_path = '/path/to/chromedriver'  # Update this with your actual path
driver = webdriver.Chrome()

# Open the Workday job site
driver.get(
    "https://www.teamworkonline.com/basketball-jobs/cleveland-cavaliers/cleveland-cavaliers-jobs"
)

# Wait for the job listings to load (adjust the waiting time if necessary)
try:
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.CLASS_NAME, "organization-portal__job-details")
        )
    )
except:
    print("Failed to load job listings")
    driver.quit()
    exit()

# Scroll down to load more jobs (adjust the range as necessary)
# for _ in range(5):  # Adjust range for more scrolls
#     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#     time.sleep(2)  # Adjust sleep time if necessary

# Parse the page source with BeautifulSoup
# soup = BeautifulSoup(driver.page_source, 'html.parser')

jobs_rows = []
jobs = [
    job
    for job in driver.find_elements(By.CLASS_NAME, "organization-portal__job-title")
    if any(keyword in job.text.lower() for keyword in KEYWORDS)
]

jobs_rows = [
    {
        "title": job.find_element(By.TAG_NAME, "a").text,
        "url": job.find_element(By.TAG_NAME, "a").get_attribute("href"),
    }
    for job in jobs
]


recent_urls = utils.get_recent_urls()

for job in jobs_rows:
    try:
        # Extract job details
        driver.get(job["url"])
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "opportunity-preview__body"))
        )

        info_elements = driver.find_elements(
            By.CLASS_NAME, "opportunity-preview__info-content-item"
        )
        location_value = info_elements[1].text
        hours = info_elements[0].text

        description_raw = driver.find_element(
            By.CLASS_NAME, "opportunity-preview__body"
        ).get_attribute("innerHTML")
        soup = BeautifulSoup(description_raw, "html.parser")
        description = soup.get_text(separator="\n").strip()
        full_description = f"{description}"

        skills_required_format, all_skills_format = utils.get_skills_required(
            full_description
        )
        none_skill = len(skills_required_format) < 2

        if (job["url"] in recent_urls) or (none_skill):
            continue

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

        record = {
            "Name": job["title"],
            "validated": True,
            "Status": "Open",
            "Start date": current_time,
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
            "language": ["English"],
            "company": COMPANY,
            "industry": industry,
            "type": ["Permanent"],
            "hours": [hours],
            "logo": LOGO,
            "logo_permanent_url": LOGO[0].get("url"),
            "SEO:Index": "1",
        }
        table.create(record)

        # WE GET THIS FROM THE JOB POSTING
        # hours = utils.get_hours(job["title"], full_description)

        # event_day = event.find_element(By.CSS_SELECTOR, "div.UIaQzd").text
        # event_month = event.find_element(By.CSS_SELECTOR, "div.wsnHcb").text
        # img_elements = event.find_element(By.TAG_NAME, "img").get_attribute(
        #     "src"
        # )

        # # Extract the src attributes
        # # src_list = [img.get_attribute("src") for img in img_elements]
        # event_list.append(
        #     {
        #         "title": title,
        #         "event_day": event_day,
        #         "event_month": event_month,
        #         "event_data": event_data,
        #         "img": img_elements,
        #     }
        # )
    except Exception as e:
        print(f"Error extracting event: {e}")


# Close the driver
driver.quit()
