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


class MLB_Teamworkonline(base_scraper.teamworkonline.TeamworkOnlineScraper):
    company_from_job_page = True
    sport_list = ["Baseball"]

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


class TorontoBlueJays(base_scraper.teamworkonline.TeamworkOnlineScraper):
    sport_list = ["Baseball"]

    def __init__(self, driver=None, keywords=None):
        super().__init__(driver=driver, keywords=keywords)
        self.company = "Toronto Blue Jays"
        self.logo = [
            {
                "url": "https://cf-production.teamworkonline.com/uploads/public/embed_d14a9392-b4ab-4ce7-8e6a-8e36e310dbde.png",
                "filename": "torontobluejays.png",
            }
        ]
        self.base_url = "https://www.teamworkonline.com/baseball-jobs/toronto-blue-jays-jobs/toronto-blue-jays"


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
    team_instance = MLB_Teamworkonline(driver=driver)
    team_instance.base_url = f"https://www.teamworkonline.com/baseball-jobs/baseballjobs/major-league-baseball?employment_opportunity_search%5Bcareer_level_id%5D=&employment_opportunity_search%5Bcategory_id%5D=&employment_opportunity_search%5Borganization_id%5D=&employment_opportunity_search%5Bquery%5D=&page={page}"
    team_instance.main()

teams = [
    TorontoBlueJays,
]

for team in teams:
    # try:
    print(f"Running {team.__name__} main()")
    team_instance = team(driver=driver)
    team_instance.main()
driver.quit()
