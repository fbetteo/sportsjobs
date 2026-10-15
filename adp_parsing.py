from urllib.parse import urlencode

ADP_DOMAIN = "workforcenow.adp.com"
RECRUITMENT_PAGE_URL = (
    f"https://{ADP_DOMAIN}/mascsr/default/mdf/recruitment/recruitment.html"
)


def public_job_url(cid: str, cc_id: str, external_job_id: str) -> str:
    """Return the shareable career-center link for one ADP job."""
    params = {
        "cid": cid,
        "ccId": cc_id,
        "jobId": external_job_id,
        "lang": "en_US",
        "selectedMenuKey": "CurrentOpenings",
    }
    return f"{RECRUITMENT_PAGE_URL}?{urlencode(params)}"


def external_job_id(requisition: dict) -> str | None:
    """Return the ID used in public ADP links (not the API itemID)."""
    string_fields = requisition.get("customFieldGroup", {}).get("stringFields", [])
    for field in string_fields:
        if field.get("nameCode", {}).get("codeValue") == "ExternalJobID":
            return field.get("stringValue") or None
    return None


def format_locations(requisition: dict) -> str:
    locations = []
    for location in requisition.get("requisitionLocations") or []:
        name = (location.get("nameCode", {}).get("shortName") or "").strip()
        if name and name not in locations:
            locations.append(name)
    return "; ".join(locations)


def minimum_salary(requisition: dict) -> str | None:
    """Format the posted minimum like utils.extract_salary does, e.g. "$95,000"."""
    minimum_rate = requisition.get("payGradeRange", {}).get("minimumRate", {})
    amount = minimum_rate.get("amountValue")
    if not amount:
        return None
    if minimum_rate.get("currencyCode", "USD") == "USD":
        return f"${amount:,.0f}"
    return f"{amount:,.0f} {minimum_rate['currencyCode']}"
