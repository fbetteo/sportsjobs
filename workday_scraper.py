from datetime import date

import markdownify
import requests

import base_scraper.companyscraper
from hetzner_utils import get_urls_by_domain, start_postgres_connection
from job_titles import title_matches_keywords
from workday_parsing import (
    canonicalize_workday_url,
    is_active_posting,
)

COMPANIES = {
    "Tennis Australia": {
        "host": "tennis.wd3.myworkdayjobs.com",
        "tenant": "tennis",
        "site": "ta_careers",
        "logo": [
            {
                "url": "https://upload.wikimedia.org/wikipedia/en/4/41/Tennis_Australia.png",
                "filename": "tennis_australia.png",
            }
        ],
        "sport_list": ["Tennis"],
    },
    "Razer": {
        "host": "razer.wd3.myworkdayjobs.com",
        "tenant": "razer",
        "site": "Careers",
        "logo": [
            {
                "url": "https://upload.wikimedia.org/wikipedia/commons/5/52/Razer_wordmark.svg",
                "filename": "razer.svg",
            }
        ],
        "industry": ["Esports"],
    },
    "xboxgaming": {
        "host": "xboxgaming.wd1.myworkdayjobs.com",
        "tenant": "xboxgaming",
        "site": "King_External_Careers",
        "logo": [
            {
                "url": "https://xboxgaming.wd1.myworkdayjobs.com/King_External_Careers/assets/logo",
                "filename": "xboxgaming.svg",
            }
        ],
        "industry": ["Esports"],
    },
    "New York Mets": {
        "host": "sterlingmets.wd5.myworkdayjobs.com",
        "tenant": "sterlingmets",
        "site": "Mets",
        "logo": [
            {
                "url": "https://upload.wikimedia.org/wikipedia/en/7/7b/New_York_Mets.svg",
                "filename": "new_york_mets.svg",
            }
        ],
        "sport_list": ["Baseball"],
    },
    "DraftKings": {
        "host": "draftkings.wd1.myworkdayjobs.com",
        "tenant": "draftkings",
        "site": "DraftKings",
        "logo": [
            {
                "url": "https://upload.wikimedia.org/wikipedia/en/a/a0/DraftKings_logo.svg",
                "filename": "draftkings.svg",
            }
        ],
    },
    "NBA": {
        "host": "nba.wd108.myworkdayjobs.com",
        "tenant": "nba",
        "site": "nbacareers",
        "logo": [
            {
                "url": "https://upload.wikimedia.org/wikipedia/en/0/03/National_Basketball_Association_logo.svg",
                "filename": "nba.svg",
            }
        ],
        "sport_list": ["Basketball"],
    },
    "BetMGM": {
        "host": "betmgminc.wd5.myworkdayjobs.com",
        "tenant": "betmgminc",
        "site": "BetMGM",
        "logo": [
            {
                "url": "https://betmgminc.wd5.myworkdayjobs.com/BetMGM/assets/logo",
                "filename": "betmgm.png",
            }
        ],
    },
    "Formula 1": {
        "host": "formulaone.wd3.myworkdayjobs.com",
        "tenant": "formulaone",
        "site": "F1",
        "logo": [
            {
                "url": "https://formulaone.wd3.myworkdayjobs.com/F1/assets/logo",
                "filename": "formula1.png",
            }
        ],
    },
    "Alpine F1 Team": {
        "host": "alliancewd.wd3.myworkdayjobs.com",
        "tenant": "alliancewd",
        "site": "alpine-racing-careers",
        "logo": [
            {
                "url": "https://upload.wikimedia.org/wikipedia/commons/4/4a/BWT_Alpine_F1_Team_Logo.png",
                "filename": "alpine_f1.png",
            }
        ],
    },
    "NASCAR": {
        "host": "nascar.wd1.myworkdayjobs.com",
        "tenant": "nascar",
        "site": "NASCAR",
        "logo": [
            {
                "url": "https://nascar.wd1.myworkdayjobs.com/NASCAR/assets/logo",
                "filename": "nascar.jpg",
            }
        ],
    },
    "PGA TOUR": {
        "host": "pgatour.wd5.myworkdayjobs.com",
        "tenant": "pgatour",
        "site": "PGATOUREXTERNAL",
        "logo": [
            {
                "url": "https://pgatour.wd5.myworkdayjobs.com/PGATOUREXTERNAL/assets/logo",
                "filename": "pga_tour.png",
            }
        ],
        "sport_list": ["Golf"],
    },
    "PGA of America": {
        "host": "pgahq.wd1.myworkdayjobs.com",
        "tenant": "pgahq",
        "site": "PGAHQ",
        "logo": [
            {
                "url": "https://pgahq.wd1.myworkdayjobs.com/PGAHQ/assets/logo",
                "filename": "pga_of_america.jpg",
            }
        ],
        "sport_list": ["Golf"],
    },
    "Detroit Red Wings": {
        "host": "ilitch.wd5.myworkdayjobs.com",
        "tenant": "ilitch",
        "site": "Detroit-Red-Wings",
        "logo": [
            {
                "url": "https://upload.wikimedia.org/wikipedia/en/e/e0/Detroit_Red_Wings_logo.svg",
                "filename": "detroit_red_wings.svg",
            }
        ],
        "sport_list": ["Hockey"],
    },
    "MLSE": {
        "host": "mlse.wd3.myworkdayjobs.com",
        "tenant": "mlse",
        "site": "MLSE",
        "logo": [
            {
                "url": "https://upload.wikimedia.org/wikipedia/en/4/45/Maple_Leaf_Sports_%26_Entertainment_logo.svg",
                "filename": "mlse.svg",
            }
        ],
    },
    "Paris Saint-Germain": {
        "host": "parissaintgermain.wd3.myworkdayjobs.com",
        "tenant": "parissaintgermain",
        "site": "rejoigneznous",
        "logo": [
            {
                "url": "https://parissaintgermain.wd3.myworkdayjobs.com/rejoigneznous/assets/logo",
                "filename": "psg.png",
            }
        ],
        "sport_list": ["Football - Soccer"],
    },
    "Aston Villa": {
        "host": "avfc.wd502.myworkdayjobs.com",
        "tenant": "avfc",
        "site": "avfc_careers",
        "logo": [
            {
                "url": "https://avfc.wd502.myworkdayjobs.com/avfc_careers/assets/logo",
                "filename": "aston_villa.png",
            }
        ],
        "sport_list": ["Football - Soccer"],
    },
    "Southampton FC": {
        "host": "saintsfc.wd3.myworkdayjobs.com",
        "tenant": "saintsfc",
        "site": "SFC001",
        "logo": [
            {
                "url": "https://saintsfc.wd3.myworkdayjobs.com/SFC001/assets/logo",
                "filename": "southampton.png",
            }
        ],
        "sport_list": ["Football - Soccer"],
    },
    "Brentford FC": {
        "host": "brentfordfootballclub.wd107.myworkdayjobs.com",
        "tenant": "brentfordfootballclub",
        "site": "BrentfordFC",
        "logo": [
            {
                "url": "https://upload.wikimedia.org/wikipedia/en/2/2a/Brentford_FC_crest.svg",
                "filename": "brentford.svg",
            }
        ],
        "sport_list": ["Football - Soccer"],
    },
    "Exos": {
        "host": "exos.wd501.myworkdayjobs.com",
        "tenant": "exos",
        "site": "EXOSCAREERS",
        "logo": [
            {
                "url": "https://www.teamexos.com/hubfs/EXOS%20LOGO_RGB-BLACK.png",
                "filename": "exos.png",
            }
        ],
    },
    "Nike": {
        "host": "nike.wd1.myworkdayjobs.com",
        "tenant": "nike",
        "site": "nke",
        "logo": [
            {
                "url": "https://nike.wd1.myworkdayjobs.com/nke/assets/logo",
                "filename": "nike.jpg",
            }
        ],
    },
    "AMB Sports & Entertainment": {
        "host": "ambgroup.wd1.myworkdayjobs.com",
        "tenant": "ambgroup",
        "site": "AMBSE",
        "logo": [
            {
                "url": "https://ambgroup.wd1.myworkdayjobs.com/AMBSE/assets/logo",
                "filename": "amb_sports.jpg",
            }
        ],
    },
    "Atlanta Braves": {
        "host": "atlantabravesmlb.wd5.myworkdayjobs.com",
        "tenant": "atlantabravesmlb",
        "site": "AtlantaBraves",
        "logo": [
            {
                "url": "https://atlantabravesmlb.wd5.myworkdayjobs.com/AtlantaBraves/assets/logo",
                "filename": "atlanta_braves.jpg",
            }
        ],
        "sport_list": ["Baseball"],
    },
    "Anaheim Ducks": {
        "host": "anaheimducks.wd5.myworkdayjobs.com",
        "tenant": "anaheimducks",
        "site": "ADHCTW",
        "logo": [
            {
                "url": "https://anaheimducks.wd5.myworkdayjobs.com/ADHCTW/assets/logo",
                "filename": "anaheim_ducks.png",
            }
        ],
        "sport_list": ["Hockey"],
    },
    "Vinik Sports Group": {
        "host": "vsg.wd1.myworkdayjobs.com",
        "tenant": "vsg",
        "site": "VSG",
        "logo": [
            {
                "url": "https://vsg.wd1.myworkdayjobs.com/VSG/assets/logo",
                "filename": "vinik_sports_group.png",
            }
        ],
        "sport_list": ["Hockey"],
    },
}


class WorkdayCompanyScraper(base_scraper.companyscraper.CompanyScraper):
    PAGE_SIZE = 20
    REQUEST_TIMEOUT = 30

    def __init__(self, company, attributes, existing_urls, session=None):
        super().__init__(driver=None, existing_urls=existing_urls)
        self.company = company
        self.host = attributes["host"]
        self.tenant = attributes["tenant"]
        self.site = attributes["site"]
        self.logo = attributes["logo"]
        self.sport_list = attributes.get("sport_list")
        self.industry = attributes.get("industry")
        self.session = session or requests.Session()
        self.keywords = [*self.keywords, "ai"]
        self.existing_urls = {
            canonicalize_workday_url(url) for url in existing_urls if url
        }
        # CompanyScraper performs a second duplicate check before insertion.
        self.recent_urls = list(self.existing_urls)

    @property
    def listing_api_url(self):
        return f"https://{self.host}/wday/cxs/{self.tenant}/{self.site}/jobs"

    def detail_api_url(self, external_path):
        return (
            f"https://{self.host}/wday/cxs/" f"{self.tenant}/{self.site}{external_path}"
        )

    def public_job_url(self, external_path):
        return canonicalize_workday_url(
            f"https://{self.host}/{self.site}{external_path}"
        )

    def open_site(self):
        # Workday exposes the same data through its public JSON endpoint.
        return None

    def get_jobs_available(self):
        jobs = []
        seen_urls = set()
        offset = 0
        total = None

        while total is None or offset < total:
            response = self.session.post(
                self.listing_api_url,
                json={
                    "appliedFacets": {},
                    "limit": self.PAGE_SIZE,
                    "offset": offset,
                    "searchText": "",
                },
                timeout=self.REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            payload = response.json()
            total = payload.get("total", 0)
            postings = payload.get("jobPostings", [])
            if not postings:
                break

            for posting in postings:
                title = posting.get("title", "").strip()
                external_path = posting.get("externalPath", "")
                if not title or not external_path:
                    continue
                if not title_matches_keywords(title, self.keywords):
                    continue

                url = self.public_job_url(external_path)
                if url in seen_urls or url in self.existing_urls:
                    continue

                seen_urls.add(url)
                jobs.append(
                    {
                        "title": title,
                        "url": url,
                        "external_path": external_path,
                    }
                )

            offset += len(postings)

        print(
            f"Found {len(jobs)} new matching Workday jobs "
            f"for {self.company} ({total or 0} active listings checked)"
        )
        return jobs

    def _scrape_job(self, job):
        try:
            response = self.session.get(
                self.detail_api_url(job["external_path"]),
                timeout=self.REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            job_info = response.json().get("jobPostingInfo", {})

            if not is_active_posting(job_info, today=date.today()):
                print(f"Skipping inactive Workday job: {job['title']}")
                return None

            canonical_url = canonicalize_workday_url(
                job_info.get("externalUrl") or job["url"]
            )
            if canonical_url in self.existing_urls:
                return None
            job["url"] = canonical_url

            description_html = job_info.get("jobDescription") or ""
            full_description = markdownify.markdownify(
                description_html,
                heading_style="ATX",
            )

            locations = [job_info.get("location", "")]
            locations.extend(job_info.get("additionalLocations") or [])
            location_value = ", ".join(
                dict.fromkeys(location for location in locations if location)
            )

            country = (job_info.get("country") or {}).get("descriptor")
            requisition_location = job_info.get("jobRequisitionLocation") or {}
            country_code = (requisition_location.get("country") or {}).get("alpha2Code")
            other_data = {"company": self.company}
            if country:
                other_data["country"] = country.lower()
            if country_code:
                other_data["country_code"] = country_code.upper()
            if self.sport_list is not None:
                other_data["sport_list"] = self.sport_list
            if self.industry is not None:
                other_data["industry"] = self.industry

            return {
                "job": job,
                "location_value": location_value,
                "hours": job_info.get("timeType") or "Full-time",
                "full_description": full_description,
                "other_data": other_data,
            }
        except (
            requests.RequestException,
            AttributeError,
            KeyError,
            TypeError,
            ValueError,
        ) as error:
            print(f"Error fetching Workday job {job['url']}: {error}")
            return None


def get_existing_workday_urls():
    conn = start_postgres_connection()
    try:
        with conn as conn:
            return get_urls_by_domain(conn, "myworkdayjobs.com")
    finally:
        if conn and conn.closed == 0:
            conn.close()
            print("Connection closed.")


def main():
    existing_urls = get_existing_workday_urls()
    for company, attributes in COMPANIES.items():
        print(f"Running Workday scraper for {company}")
        scraper = WorkdayCompanyScraper(
            company,
            attributes,
            existing_urls=existing_urls,
        )
        try:
            scraper.main()
        finally:
            scraper.session.close()


if __name__ == "__main__":
    main()
