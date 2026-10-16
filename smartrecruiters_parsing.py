SMARTRECRUITERS_DOMAIN = "jobs.smartrecruiters.com"
DESCRIPTION_SECTIONS = (
    "jobDescription",
    "qualifications",
    "additionalInformation",
)


def public_job_url(company_identifier: str, posting_id: str) -> str:
    """Return a stable job link; SmartRecruiters' own links append a title slug."""
    return f"https://{SMARTRECRUITERS_DOMAIN}/{company_identifier}/{posting_id}"


def description_html(job_ad: dict) -> str:
    sections = job_ad.get("sections", {})
    parts = []
    for key in DESCRIPTION_SECTIONS:
        section = sections.get(key) or {}
        text = section.get("text")
        if text:
            parts.append(f"<h2>{section.get('title', '')}</h2>{text}")
    return "".join(parts)


def location_fields(location: dict) -> dict:
    """Return location text plus country fields in the shape CompanyScraper expects."""
    # fullLocation leaves an empty slot for a missing region: "Ljubljana, , Slovenia".
    parts = (location.get("fullLocation") or "").split(",")
    full_location = ", ".join(part.strip() for part in parts if part.strip())
    fields = {"location_value": full_location}
    country_code = location.get("country")
    if country_code and full_location:
        fields["country"] = full_location.split(",")[-1].strip().lower()
        fields["country_code"] = country_code.upper()
    if location.get("remote") or location.get("hybrid"):
        work_mode = "Remote" if location.get("remote") else "Hybrid"
        fields["location_value"] = f"{full_location}, {work_mode}".strip(", ")
        fields["remote"] = "Yes"
    return fields
