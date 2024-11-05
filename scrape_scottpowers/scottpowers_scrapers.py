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
import markdownify
import utils


# replace SportJobs with the name of the site or a relevant identifier in the class name
class ScottPowersScraper(base_scraper.companyscraper.CompanyScraper):

    def __init__(self, driver=None, keywords=None):
        super().__init__(driver=driver, keywords=keywords)
        self.company = "SportsJobs"
        self.logo = [
            {
                "url": "https://example.com/path/to/logo.png",
                "filename": "sportsjobs.png",
            }
        ]
        self.base_url = "https://saberpowers.github.io/jobs/"
        self.linkedin_login_url = "https://www.linkedin.com/login"

    def open_site(self):
        try:
            # Open LinkedIn login page
            self.driver.get(self.linkedin_login_url)

            # Wait for login fields to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )

            # Enter credentials
            username_input = self.driver.find_element(By.ID, "username")
            password_input = self.driver.find_element(By.ID, "password")
            username_input.send_keys(os.getenv("LINKEDIN_USERNAME"))
            password_input.send_keys(os.getenv("LINKEDIN_PASSWORD"))

            # Click login button
            self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

            # Wait for main LinkedIn page to load post-login
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "global-nav"))
            )
            print("Logged into LinkedIn successfully")

        except Exception as e:
            print("LinkedIn login failed:", e)
            exit()

        self.driver.get(self.base_url)

        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "DataTables_Table_0"))
            )
        except:
            print("Failed to load job listings")
            exit()

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

                    # Filter by keywords
                    if any(
                        keyword.lower() in title.lower() for keyword in self.keywords
                    ):
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

        try:
            # Navigate to the job URL
            self.driver.get(job["url"])

            # Wait for the job description container to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, "jobs-description__container")
                )
            )

            # Click the "See more" button to expand the full job description, if it exists
            try:
                see_more_button = self.driver.find_element(
                    By.CLASS_NAME, "jobs-description__footer-button"
                )
                if see_more_button.is_displayed():
                    see_more_button.click()
            except Exception as e:
                print("See more button not found or could not be clicked:", e)

            # Wait for the description content to fully load and retrieve the raw HTML
            description_container = self.driver.find_element(
                By.CLASS_NAME, "jobs-box__html-content"
            )
            description_raw = description_container.get_attribute("innerHTML")

            # Convert the description HTML to Markdown format
            full_description = markdownify.markdownify(
                description_raw, heading_style="ATX"
            )

            # Mock location and hours, replace with real data if available on the page
            try:
                location_element = self.driver.find_element(
                    By.CLASS_NAME,
                    "job-details-jobs-unified-top-card__primary-description-container",
                )
                location_value = location_element.find_element(
                    By.CSS_SELECTOR, "span.tvm__text--low-emphasis"
                ).text
            except Exception as e:
                print("Location not found:", e)
                location_value = "Not specified"

            hours = "Full-time"

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

        except Exception as e:
            print(f"Error extracting job details: {e}")
            return None

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

        if job["url"] in self.recent_urls:
            return None

        country = utils.find_country(location_value)["country"]
        country_code = utils.find_country(location_value)["country_code"]
        accepts_remote = utils.get_remote_status(
            full_description, location_value, job["title"]
        )
        hours = utils.get_hours(job["title"], full_description, hours)
        remote_office = utils.is_remote_global(full_description)
        job_area = utils.add_job_area(skills_required_format)

        seniority = utils.get_seniority_level(job["title"])
        # override with data from the table for internship. The others are not so reliable
        if job["stage"] == "Internship":
            seniority = "Internship"
        industry = utils.add_industry(job["title"], full_description)
        sport_list = utils.add_sport_list(job["title"], full_description)

        try:
            salary = utils.extract_salary(full_description)[0]
        except:
            salary = None

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


# # For debug
# driver = webdriver.Chrome()
# aa = ScottPowersScraper(driver=driver)

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
print(f"Running ScottPowersScraper main()")
team_instance = ScottPowersScraper(driver=driver)
team_instance.main()
driver.quit()
