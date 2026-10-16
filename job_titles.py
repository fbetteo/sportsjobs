import re

# Title words for the Greenhouse and Ashby scrapers, which read every job on a
# board. Product, sales, legal and finance titles are left out on purpose.
TECH_TITLE_KEYWORDS = [
    "data",
    "analyst",
    "analytics",
    "scientist",
    "science",
    "sciences",
    "engineer",
    "engineering",
    "software engineer",
    "developer",
    "programmer",
    "machine learning",
    "deep learning",
    "artificial intelligence",
    "ai",
    "ml",
    "business intelligence",
    "researcher",
    "quant",
    "quantitative",
    "modeler",
    "modeller",
    "statistician",
    "statistics",
    "trader",
    "trading",
    "intern",
    "internship",
]


def title_matches_keywords(title: str, keywords: list[str]) -> bool:
    for keyword in keywords:
        pattern = rf"(?<!\w){re.escape(keyword)}(?!\w)"
        if re.search(pattern, title, flags=re.IGNORECASE):
            return True
    return False
