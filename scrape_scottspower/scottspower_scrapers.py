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
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class ScottPowersScraper2(base_scraper.companyscraper.CompanyScraper):

    def __init__(self, driver=None, keywords=None):
        super().__init__(driver=driver, keywords=keywords)
        self.company = ""
        self.logo = [
            {
                "url": "",
                "filename": "",
            }
        ]
        self.base_url = "https://saberpowers.github.io/jobs/"

    def open_site(self):
        self.driver.get(self.base_url)

        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "DataTables_Table_0"))
            )
        except:
            print("Failed to load job listings")
            raise Exception(
                "Failed to load job listings"
            )  # Raise exception instead of exit

    def get_jobs_available(self):
        jobs_rows = []
        while True:
            # Get the job rows in the current page
            jobs = self.driver.find_elements(
                By.CSS_SELECTOR, "#DataTables_Table_0 tbody tr"
            )

            # Extract job details
            for job in jobs:
                try:
                    title_element = job.find_element(
                        By.CSS_SELECTOR, "td:nth-child(4) a"
                    )

                    title = title_element.text
                    url = title_element.get_attribute("href")
                    team_element = job.find_element(By.CSS_SELECTOR, "td:nth-child(3)")
                    team = team_element.text
                    logo_url = team_element.find_element(
                        By.TAG_NAME, "img"
                    ).get_attribute("src")

                    discipline = job.find_element(
                        By.CSS_SELECTOR, "td:nth-child(5)"
                    ).text
                    stage = job.find_element(By.CSS_SELECTOR, "td:nth-child(6)").text
                    sport = job.find_element(By.CSS_SELECTOR, "td:nth-child(7)").text

                    # Don't Filter by keywords. The site has good job posts
                    # if any(
                    #     keyword.lower() in title.lower() for keyword in self.keywords
                    # ):
                    jobs_rows.append(
                        {
                            "title": title,
                            "url": url,
                            "team": team,
                            "logo": [
                                {
                                    "url": logo_url,
                                    "filename": f"{team}.png",
                                }
                            ],
                            "discipline": discipline,
                            "stage": stage,
                            "sport": sport,
                        }
                    )
                except Exception as e:
                    print(f"Error processing job entry: {e}")
            break

            # Check if there's a next page and navigate to it
            # Commenting because we want to check just today
            # try:
            #     next_button = self.driver.find_element(By.ID, "DataTables_Table_0_next")
            #     if "disabled" in next_button.get_attribute("class"):
            #         break  # No more pages
            #     next_button.click()
            #     WebDriverWait(self.driver, 10).until(
            #         EC.presence_of_element_located(
            #             (By.CSS_SELECTOR, "#DataTables_Table_0 tbody tr")
            #         )
            #     )
            # except:
            #     print("Failed to load the next page of job listings")
            #     break

        return jobs_rows

    def _scrape_job(self, job):
        if "linkedin" not in job["url"]:
            print("Not a linkedin job, I need to handle those differently")
            return None

        # Try to get job data from GhostGenius API for LinkedIn jobs
        linkedin_job_data = self._fetch_linkedin_job_via_api(job["url"])
        if linkedin_job_data:
            return self._process_linkedin_api_response(linkedin_job_data, job)

        ## NOT TRYING TO GO INTO LINKEDIN FOR NOW
        # try:
        #     # Navigate to the job URL
        #     self.driver.get(job["url"])

        #     # Wait for the job description container to load
        #     WebDriverWait(self.driver, 10).until(
        #         EC.presence_of_element_located(
        #             (By.CLASS_NAME, "jobs-description__container")
        #         )
        #     )

        #     # Click the "See more" button to expand the full job description, if it exists
        #     try:
        #         see_more_button = self.driver.find_element(
        #             By.CLASS_NAME, "jobs-description__footer-button"
        #         )
        #         if see_more_button.is_displayed():
        #             see_more_button.click()
        #     except Exception as e:
        #         print("See more button not found or could not be clicked:", e)

        #     # Wait for the description content to fully load and retrieve the raw HTML
        #     description_container = self.driver.find_element(
        #         By.CLASS_NAME, "jobs-box__html-content"
        #     )
        #     description_raw = description_container.get_attribute("innerHTML")

        #     # Convert the description HTML to Markdown format
        #     full_description = markdownify.markdownify(
        #         description_raw, heading_style="ATX"
        #     )

        #     # Mock location and hours, replace with real data if available on the page
        #     try:
        #         location_element = self.driver.find_element(
        #             By.CLASS_NAME,
        #             "job-details-jobs-unified-top-card__primary-description-container",
        #         )
        #         location_value = location_element.find_element(
        #             By.CSS_SELECTOR, "span.tvm__text--low-emphasis"
        #         ).text
        #     except Exception as e:
        #         print("Location not found:", e)
        #         location_value = "Not specified"

        # Fallback to basic job data if API fails
        return self._fallback_linkedin_job_data(job)

    def _fetch_linkedin_job_via_api(self, linkedin_url: str):
        """
        Fetch LinkedIn job data using GhostGenius API

        Args:
            linkedin_url (str): The LinkedIn job URL to scrape

        Returns:
            dict: Job data from API or None if failed
        """
        api_url = "https://api.ghostgenius.fr/v2/job"

        # Get bearer token from environment variables
        bearer_token = os.getenv("GHOSTGENIUS_API_TOKEN")
        if not bearer_token:
            print("Error: GHOSTGENIUS_API_TOKEN not found in environment variables")
            return None

        headers = {"Accept": "*/*", "Authorization": f"Bearer {bearer_token}"}

        params = {"url": linkedin_url}

        try:
            print(f"Fetching LinkedIn job data for: {linkedin_url}")
            response = requests.get(api_url, headers=headers, params=params, timeout=30)
            response.raise_for_status()  # Raises an HTTPError for bad responses

            job_data = response.json()
            print("Successfully fetched job data from GhostGenius API")
            return job_data

        except requests.exceptions.Timeout:
            print(f"Timeout error when calling GhostGenius API for {linkedin_url}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Request error when calling GhostGenius API: {e}")
            return None
        except ValueError as e:
            print(f"JSON decode error from GhostGenius API response: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error when calling GhostGenius API: {e}")
            return None

    def _process_linkedin_api_response(self, api_response: dict, original_job: dict):
        """
        Process the API response and format it for the job pipeline

        Args:
            api_response (dict): Response from GhostGenius API
            original_job (dict): Original job data from scraper

        Returns:
            dict: Formatted job data for processing
        """
        try:
            print("Processing LinkedIn API response...")
            print(f"Job ID: {api_response.get('id', 'N/A')}")
            print(f"Job Title: {api_response.get('title', 'N/A')}")

            # Extract job information from API response
            job_title = api_response.get("title", original_job.get("title", ""))
            job_description = api_response.get("description", "")
            contract_type = api_response.get("contract_type", "Full-time")
            location = api_response.get("location", "")
            work_place = api_response.get("work_place", "")
            work_remote_allowed = api_response.get("work_remote_allowed", False)
            linkedin_url = api_response.get("url", original_job.get("url", ""))

            # Process location - combine location and work_place info
            location_parts = []
            if location:
                location_parts.append(location)
            if work_place and work_place != location:
                location_parts.append(work_place)
            if work_remote_allowed:
                location_parts.append("Remote")

            location_value = (
                ", ".join(location_parts) if location_parts else "Not specified"
            )

            # Map contract type to hours format
            hours_mapping = {
                "Full-time": "Fulltime",
                "Part-time": "Part-time",
                "Contract": "Fulltime",
                "Temporary": "Fulltime",
                "Internship": "Fulltime",
            }
            hours = hours_mapping.get(contract_type, contract_type)

            # Get company information
            company_info = api_response.get("company", {})
            company_name = company_info.get("full_name", original_job.get("team", ""))
            company_logo_url = ""

            # Extract company logo (use the largest available)
            profile_pictures = company_info.get("profile_picture", [])
            if profile_pictures:
                # Sort by size and get the largest
                largest_logo = max(
                    profile_pictures,
                    key=lambda x: x.get("width", 0) * x.get("height", 0),
                )
                company_logo_url = largest_logo.get("url", "")

            # Get apply URL - prefer company direct URL over LinkedIn easy apply
            apply_method = api_response.get("apply_method", {})
            apply_url = (
                apply_method.get("company_apply_url")
                or apply_method.get("easy_apply_url")
                or linkedin_url
            )

            # Get additional metadata
            listed_date = api_response.get("listed_at_date", "")
            job_state = api_response.get("state", "UNKNOWN")
            is_closed = api_response.get("closed", False)

            # Update job data with API information
            updated_job = original_job.copy()
            updated_job.update(
                {
                    "title": job_title,
                    "url": apply_url,  # Use apply URL instead of LinkedIn URL if available
                    "team": company_name,
                    "logo": (
                        company_logo_url
                        if company_logo_url
                        else original_job.get("logo", self.logo)
                    ),
                }
            )

            # Set logo for the scraper
            if company_logo_url:
                self.logo = [{"url": company_logo_url, "alt": company_name}]

            print(f"Successfully processed LinkedIn job: {job_title} at {company_name}")
            print(f"Location: {location_value}")
            print(f"Hours: {hours}")
            print(f"Apply URL: {apply_url}")

            return {
                "job": updated_job,
                "location_value": location_value,
                "hours": hours,
                "full_description": job_description,
                "other_data": {
                    "company": company_name,
                    "logo": updated_job["logo"],
                    "linkedin_job_id": api_response.get("id", ""),
                    "linkedin_url": linkedin_url,
                    "contract_type": contract_type,
                    "work_remote_allowed": work_remote_allowed,
                    "listed_date": listed_date,
                    "job_state": job_state,
                    "is_closed": is_closed,
                    "company_linkedin_url": company_info.get("url", ""),
                    "company_headline": company_info.get("headline", ""),
                    "apply_method": apply_method,
                    "original_linkedin_url": linkedin_url,
                    "api_source": "ghostgenius",
                },
            }

        except Exception as e:
            print(f"Error processing LinkedIn API response: {e}")
            print(
                f"API Response structure: {type(api_response)} with keys: {list(api_response.keys()) if isinstance(api_response, dict) else 'Not a dict'}"
            )
            # Fallback to original method
            return self._fallback_linkedin_job_data(original_job)

    def _fallback_linkedin_job_data(self, job: dict):
        """
        Fallback method when API fails - returns basic job data

        Args:
            job (dict): Original job data

        Returns:
            dict: Basic job data structure
        """
        hours = "Full-time"
        location_value = ""
        full_description = "To get all the details, please click Apply, you will be redirected to the linkedin job post."

        self.logo = job.get("logo", self.logo)

        return {
            "job": job,
            "location_value": location_value,
            "hours": hours,
            "full_description": full_description,
            "other_data": {
                "company": job["team"],
                "logo": job["logo"],
            },
        }

    def _enrich_and_format_job(self, job_data: dict):

        job = job_data.get("job")
        location_value = job_data.get("location_value")
        hours = job_data.get("hours")
        full_description = job_data.get("full_description")

        other_data = job_data.get("other_data", {})
        # Escape job is status is closed.
        if other_data.get("is_closed", "False"):
            print("Job is closed, skipping.")
            return None

        skills_required_format, all_skills_format = utils.get_skills_required(
            full_description
        )
        none_skill = len(skills_required_format) < 2

        if job["url"] in self.recent_urls:
            return None

        country = "united states"
        country_code = "US"
        accepts_remote = utils.get_remote_status(
            full_description, location_value, job["title"]
        )
        # hours = utils.get_hours(job["title"], full_description, hours)
        hours = job_data.get("hours", "Fulltime")
        remote_office = utils.is_remote_global(full_description)
        job_area = "Analytics"

        seniority = utils.get_seniority_level(job["title"])
        # override with data from the table for internship. The others are not so reliable
        if job["stage"] == "Internship":
            seniority = "Internship"
        industry = utils.add_industry(job["title"], full_description)
        sport_list = utils.add_sport_list(job["title"], full_description)

        try:
            salary = utils.extract_salary(full_description)[0]
        except:
            salary = ""

        return {
            "Name": job["title"],
            "url": job["url"],
            "location": location_value,
            "country": country,
            "country_code": country_code,
            "seniority": seniority,
            "desciption": full_description,
            "sport_list": sport_list,
            "skills": all_skills_format,
            "remote": accepts_remote,
            "remote_office": remote_office,
            "job_area": job_area,
            "salary": str(salary),
            "industry": industry,
            "hours": [hours],
        } | other_data


chrome_options = Options()
# required with the current docker image
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--remote-debugging-port=9222")
chrome_options.add_argument("--disable-gpu")

driver = webdriver.Chrome(options=chrome_options)


teams = [
    ScottPowersScraper2,
]

for team in teams:
    # try:
    print(f"Running {team.__name__} main()")
    team_instance = team(driver=driver)
    team_instance.main()
driver.quit()
