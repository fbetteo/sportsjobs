import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import base_scraper.companyscraper
import base_scraper.teamworkonline
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import markdownify


class MOTORSPORTS_Teamworkonline(base_scraper.teamworkonline.TeamworkOnlineScraper):
    company_from_job_page = True
    sport_list = ["Motorsports"]

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


chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--remote-debugging-port=9222")
chrome_options.add_argument("--disable-gpu")

driver = webdriver.Chrome(options=chrome_options)

page = 0
while page < 2:
    page += 1
    print(f"Running TeamworkOnline page {page} ")
    team_instance = MOTORSPORTS_Teamworkonline(driver=driver)
    team_instance.base_url = f"https://www.teamworkonline.com/motorsports-jobs/motorsports-jobs/motorsports-jobs?page={page}"
    team_instance.main()

teams = []

for team in teams:
    print(f"Running {team.__name__} main()")
    team_instance = team(driver=driver)
    team_instance.main()

driver.quit()
